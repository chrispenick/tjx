# app_join.py
# Customers + Transactions Explorer (robust parsing, merge status, flexible segment support)

import io, csv, traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from pandas.errors import EmptyDataError, ParserError

# =========================
# Page / safety
# =========================
st.set_page_config(page_title="Customers + Transactions Explorer", layout="wide")
st.set_option("client.showErrorDetails", True)
st.title("Customers + Transactions Explorer")

# =========================
# Robust file loader
# =========================
def read_table_safely(
    file,
    nrows=None,
    sep_choice="auto",
    header_choice="first row is header",
    encoding_choice="utf-8",
):
    """Robust reader for CSV/TSV/TXT and XLSX (handles BOM, cp1252, sniffed delimiters)."""
    if file is None:
        return None, "No file provided.", {}

    name = getattr(file, "name", "")
    raw = file.getvalue() if hasattr(file, "getvalue") else None
    diag = {
        "name": name,
        "size_bytes": len(raw) if isinstance(raw, (bytes, bytearray)) else None,
        "head_bytes": (raw[:2048] if isinstance(raw, (bytes, bytearray)) else None),
        "sniff_delimiter": None,
        "sniff_has_header": None,
    }

    # Excel/ZIP and PDF guards
    if isinstance(raw, (bytes, bytearray)):
        if raw[:2] == b"PK":
            try:
                return pd.read_excel(io.BytesIO(raw), nrows=nrows), None, diag
            except Exception as e:
                return None, f"File looks like Excel (zip) but failed to open: {e}", diag
        if raw[:4] == b"%PDF":
            return None, "This is a PDF, not a CSV/TSV.", diag

    # Excel by extension
    if name.lower().endswith((".xlsx", ".xls")):
        try:
            return pd.read_excel(file, nrows=nrows), None, diag
        except Exception as e:
            return None, f"Failed to read Excel: {e}", diag

    sep_map = {"auto": None, "comma (,)": ",", "tab (\\t)": "\t", "semicolon (;)": ";", "pipe (|)": "|"}
    sep = sep_map.get(sep_choice, None)
    hdr = 0 if header_choice == "first row is header" else None

    # Sniff if auto
    sniff_sep = None
    sniff_has_header = None
    if isinstance(raw, (bytes, bytearray)) and sep is None:
        try:
            sample = raw[:8192].decode(encoding_choice, errors="ignore")
            sniffer = csv.Sniffer()
            sniff_sep = sniffer.sniff(sample).delimiter
            sniff_has_header = sniffer.has_header(sample)
            diag["sniff_delimiter"] = sniff_sep
            diag["sniff_has_header"] = sniff_has_header
        except Exception:
            pass

    def _try(enc, s):
        try:
            return pd.read_csv(
                io.BytesIO(raw) if isinstance(raw, (bytes, bytearray)) else file,
                nrows=nrows,
                sep=s,
                engine="python",
                header=hdr,
                encoding=enc,
                on_bad_lines="skip",
            ), None
        except EmptyDataError:
            return None, "The file appears to be empty or has no recognizable columns."
        except ParserError as e:
            return None, f"Parser error: {e}"
        except UnicodeDecodeError as e:
            return None, f"Encoding error: {e}"
        except Exception as e:
            return None, f"Read error: {e}"

    # User choice → sniffed → pandas sniff (None)
    sep_candidates = [sep] if sep is not None else [sniff_sep, None]
    enc_candidates = [encoding_choice, "utf-8-sig", "utf-8", "cp1252", "latin-1"]

    for enc in enc_candidates:
        for s in sep_candidates:
            df, err = _try(enc, s)
            if err is None and isinstance(df, pd.DataFrame) and len(df.columns) > 0:
                return df, None, diag

    # Brute-force fallbacks
    for enc in ["utf-8-sig", "cp1252", "latin-1"]:
        for s in [",", "\t", ";", "|"]:
            df, err = _try(enc, s)
            if err is None and isinstance(df, pd.DataFrame) and len(df.columns) > 0:
                return df, None, diag

    return None, "Unable to parse the file. Adjust delimiter/header/encoding.", diag

# =========================
# Helpers
# =========================
def norm(s: str) -> str:
    s = str(s)
    return "".join(s.strip().lower().replace("_", "").split())

def suggest_key(cols):
    candidates = ["customer_id", "customerid", "cust_id", "custid", "cid", "user_id", "userid", "person_id", "personid"]
    ncols = {norm(c): c for c in cols}
    for c in candidates:
        if c in ncols:
            return ncols[c]
    for c in cols:
        if norm(c).endswith("id"):
            return c
    return cols[0] if cols else None

def candidate_categoricals(df: pd.DataFrame, extra: list[str] | None = None, max_uniques: int = 50) -> list[str]:
    cols = []
    if df is None or df.empty:
        return cols
    for c in df.columns:
        if df[c].dtype == "object":
            try:
                nun = df[c].nunique(dropna=True)
                if 1 < nun <= max_uniques:
                    cols.append(c)
            except Exception:
                pass
    if extra:
        for c in extra:
            if c in df.columns and c not in cols:
                cols.append(c)
    return cols

# =========================
# UI — Uploads & parsing options
# =========================
with st.sidebar:
    st.header("Data (Sidebar)")
    tx_file = st.file_uploader("Upload transactions.csv", type=["csv", "tsv", "txt", "xlsx", "xls"], key="tx_side")
    cust_file = st.file_uploader("Upload customers.csv (optional)", type=["csv", "tsv", "txt", "xlsx", "xls"], key="cust_side")

# Mirror uploader in main (prevents blank page if sidebar hidden)
if tx_file is None:
    st.subheader("Upload transactions.csv")
    tx_file = st.file_uploader("Upload transactions.csv", type=["csv", "tsv", "txt", "xlsx", "xls"], key="tx_main")
    st.caption("Tip: If you only see a blank page, your browser may be hiding the sidebar. Click the » icon in the top-left.")

with st.sidebar:
    st.divider()
    st.header("Parsing")
    sep_choice = st.selectbox("Delimiter", ["auto", "comma (,)", "tab (\\t)", "semicolon (;)", "pipe (|)"], index=0)
    header_choice = st.selectbox("Header", ["first row is header", "no header"], index=0)
    encoding_choice = st.selectbox("Encoding", ["utf-8", "utf-8-sig", "utf-16", "cp1252", "latin-1"], index=0)

if tx_file is None:
    st.info("Waiting for a transactions file…")
    st.stop()

# Peek columns for dropdowns
tx_peek, _, _ = read_table_safely(tx_file, nrows=1, sep_choice=sep_choice, header_choice=header_choice, encoding_choice=encoding_choice)
cust_peek, _, _ = (None, None, None)
if cust_file:
    cust_peek, _, _ = read_table_safely(cust_file, nrows=1, sep_choice=sep_choice, header_choice=header_choice, encoding_choice=encoding_choice)

tx_cols_peek = list(tx_peek.columns) if isinstance(tx_peek, pd.DataFrame) else []
cust_cols_peek = list(cust_peek.columns) if isinstance(cust_peek, pd.DataFrame) else []

tx_date_default = "date" if "date" in tx_cols_peek else ("order_date" if "order_date" in tx_cols_peek else (tx_cols_peek[0] if tx_cols_peek else ""))
tx_rev_default  = "amount" if "amount" in tx_cols_peek else ("total_amount" if "total_amount" in tx_cols_peek else (tx_cols_peek[0] if tx_cols_peek else ""))
tx_id_default   = "transaction_id" if "transaction_id" in tx_cols_peek else (tx_cols_peek[0] if tx_cols_peek else "")
tx_key_suggest  = suggest_key(tx_cols_peek)
cust_key_suggest = suggest_key(cust_cols_peek)

with st.sidebar:
    st.header("Columns / Merge")
    tx_date = st.selectbox("Transactions: date column", tx_cols_peek or [tx_date_default], index=(tx_cols_peek.index(tx_date_default) if tx_cols_peek and tx_date_default in tx_cols_peek else 0))
    tx_rev  = st.selectbox("Transactions: amount/revenue column", tx_cols_peek or [tx_rev_default], index=(tx_cols_peek.index(tx_rev_default) if tx_cols_peek and tx_rev_default in tx_cols_peek else 0))
    tx_id   = st.selectbox("Transactions: transaction ID", tx_cols_peek or [tx_id_default], index=(tx_cols_peek.index(tx_id_default) if tx_cols_peek and tx_id_default in tx_cols_peek else 0))

    if tx_cols_peek:
        tx_key = st.selectbox("Transactions: customer key", tx_cols_peek, index=(tx_cols_peek.index(tx_key_suggest) if tx_key_suggest in tx_cols_peek else 0))
    else:
        tx_key = st.text_input("Transactions: customer key", value="customer_id")

    if cust_cols_peek:
        cust_key = st.selectbox("Customers: customer key", cust_cols_peek, index=(cust_cols_peek.index(cust_key_suggest) if cust_key_suggest in cust_cols_peek else 0))
    else:
        cust_key = st.text_input("Customers: customer key", value="customer_id")

    merge_how = st.selectbox("Merge type", ["left (keep all transactions)", "inner (only matched)"], index=0)

# =========================
# Main app (guarded)
# =========================
def main():
    # Load full transactions
    tx, tx_err, tx_diag = read_table_safely(tx_file, sep_choice=sep_choice, header_choice=header_choice, encoding_choice=encoding_choice)

    with st.expander("File diagnostics (transactions)"):
        st.write({k: tx_diag.get(k) for k in ["name", "size_bytes", "sniff_delimiter", "sniff_has_header"]})
        hb = tx_diag.get("head_bytes")
        if isinstance(hb, (bytes, bytearray)):
            st.code(hb[:1000].decode("utf-8", errors="ignore"), language="text")

    if tx_err:
        st.error(f"Transactions file error: {tx_err}")
        return
    if not isinstance(tx, pd.DataFrame) or tx.empty:
        st.error("Transactions file appears empty after parsing.")
        return

    # Basic typing
    if tx_date in tx.columns:
        tx["_tx_dt"] = pd.to_datetime(tx[tx_date], errors="coerce", infer_datetime_format=True)
    else:
        tx["_tx_dt"] = pd.NaT

    if tx_rev in tx.columns:
        tx[tx_rev] = pd.to_numeric(tx[tx_rev], errors="coerce")

    tx = tx.drop_duplicates()
    merged = tx.copy()
    used_customers = False
    merge_stats = {}

    # Load/merge customers (optional)
    cust = None
    if cust_file:
        cust, cust_err, cust_diag = read_table_safely(cust_file, sep_choice=sep_choice, header_choice=header_choice, encoding_choice=encoding_choice)

        with st.expander("File diagnostics (customers)"):
            st.write({k: cust_diag.get(k) for k in ["name", "size_bytes", "sniff_delimiter", "sniff_has_header"]})
            hb = cust_diag.get("head_bytes")
            if isinstance(hb, (bytes, bytearray)):
                st.code(hb[:1000].decode("utf-8", errors="ignore"), language="text")

        if cust_err:
            st.warning(f"Customers file warning: {cust_err}")
        elif isinstance(cust, pd.DataFrame) and not cust.empty:
            missing = []
            if tx_key not in tx.columns:
                missing.append(f"Transactions missing key: `{tx_key}`")
            if cust_key not in cust.columns:
                missing.append(f"Customers missing key: `{cust_key}`")
            if missing:
                st.warning(" / ".join(missing) + " — update the key dropdowns in the sidebar.")
            else:
                merged[tx_key] = merged[tx_key].astype("string")
                cust[cust_key] = cust[cust_key].astype("string")
                how = "left" if merge_how.startswith("left") else "inner"
                merged = merged.merge(cust, left_on=tx_key, right_on=cust_key, how=how, suffixes=("", "_cust"))
                used_customers = True

                # Merge status: matched vs unmatched
                merge_stats["transactions"] = len(tx)
                merge_stats["customers"] = cust[cust_key].nunique()
                merge_stats["matched_rows"] = merged[tx_key].notna().sum()
                merge_stats["matched_customers"] = merged[cust_key].notna().sum() if cust_key in merged.columns else np.nan
                merge_stats["coverage_%"] = round(100 * merge_stats["matched_rows"] / max(1, merge_stats["transactions"]), 2)

    # Merge status panel
    with st.container():
        cols = st.columns(4)
        cols[0].metric("Transactions rows", f"{len(tx):,}")
        if used_customers and merge_stats:
            cols[1].metric("Unique customers (file)", f"{merge_stats['customers']:,}")
            cols[2].metric("Matched rows", f"{merge_stats['matched_rows']:,}")
            cols[3].metric("Coverage", f"{merge_stats['coverage_%']}%")
        else:
            cols[1].metric("Customers uploaded", "No")
            cols[2].metric("Matched rows", "—")
            cols[3].metric("Coverage", "—")

    # Filters
    with st.sidebar:
        st.header("Filters")

        # Date range uses parsed _tx_dt
        start = end = None
        dt_series = merged["_tx_dt"] if "_tx_dt" in merged.columns else pd.Series(pd.NaT, index=merged.index)
        if dt_series.notna().any():
            mind, maxd = dt_series.min(), dt_series.max()
            start, end = st.date_input("Date range", value=(mind.date(), maxd.date()))
        else:
            st.caption("No parseable dates found. Choose the correct date column or check file format.")

        # Category filter: include common tx fields + customer fields
        cat_fields = []
        # Explicitly support customer_segment + common names
        for c in ["customer_segment", "segment", "tier", "region"]:
            if c in merged.columns and c not in cat_fields:
                cat_fields.append(c)
        # Include any object dtype with ≤ 50 uniques
        cat_auto = candidate_categoricals(merged, extra=None, max_uniques=50)
        for c in cat_auto:
            if c not in cat_fields:
                cat_fields.append(c)
        # Always offer common tx fields if present
        for c in ["channel", "source", "store_id"]:
            if c in merged.columns and c not in cat_fields:
                cat_fields.append(c)

        chosen_cat = st.selectbox("Filter by field (optional)", ["(None)"] + cat_fields) if cat_fields else "(None)"
        chosen_val = None
        if chosen_cat != "(None)":
            vals = ["(All)"] + sorted(merged[chosen_cat].dropna().astype(str).unique().tolist())
            chosen_val = st.selectbox(f"{chosen_cat} value", vals, index=0)

    # Apply filters
    mask = pd.Series(True, index=merged.index)
    if start and end and "_tx_dt" in merged.columns:
        mask &= merged["_tx_dt"].between(pd.to_datetime(start), pd.to_datetime(end))
    if chosen_cat != "(None)" and chosen_val and chosen_val != "(All)":
        mask &= merged[chosen_cat].astype(str).eq(chosen_val)

    data = merged.loc[mask].copy()

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    total_rev = np.nansum(data[tx_rev]) if tx_rev in data.columns else np.nan
    tx_count = len(data[tx_id].dropna()) if tx_id in data.columns else len(data)
    unique_cust = data[tx_key].nunique() if tx_key in data.columns else np.nan
    aov = (total_rev / tx_count) if tx_count and not np.isnan(total_rev) else np.nan

    k1.metric("Total Revenue", f"${total_rev:,.2f}" if pd.notna(total_rev) else "—")
    k2.metric("Transactions", f"{tx_count:,}")
    k3.metric("Unique Customers", f"{unique_cust:,}" if pd.notna(unique_cust) else "—")
    k4.metric("Avg Order Value", f"${aov:,.2f}" if pd.notna(aov) else "—")

    st.divider()

    # Chart 1: Revenue over Time
    st.subheader("Revenue over Time")
    left, right = st.columns([2, 1])
    with right:
        freq = st.selectbox("Resample", ["D - Daily", "W - Weekly", "M - Monthly"], index=2)
        freq_code = freq.split(" - ")[0][0]  # D/W/M

    if "_tx_dt" in data.columns and tx_rev in data.columns and data["_tx_dt"].notna().any():
        ts = (
            data[["_tx_dt", tx_rev]]
            .dropna(subset=["_tx_dt", tx_rev])
            .set_index("_tx_dt")
            .sort_index()
            .resample(freq_code)[tx_rev]
            .sum()
        )
        fig1, ax1 = plt.subplots()
        ts.plot(ax=ax1)
        ax1.set_ylabel("Revenue")
        ax1.set_xlabel("Date")
        st.pyplot(fig1)
    else:
        st.info("Select the correct date and revenue columns in the sidebar to plot the time series.")

    st.divider()

    # Chart 2: Distribution / Relationship
    st.subheader("Distribution / Relationship")
    num_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    mode = st.radio("Chart type", ["Boxplot (distribution)", "Scatter (relationship)"], horizontal=True)

    if mode == "Boxplot (distribution)":
        if not num_cols:
            st.info("No numeric columns found.")
        else:
            ycol = st.selectbox("Numeric column", num_cols, index=0)
            fig2, ax2 = plt.subplots()
            sns.boxplot(y=data[ycol], ax=ax2)
            ax2.set_ylabel(ycol)
            st.pyplot(fig2)
    else:
        if len(num_cols) < 2:
            st.info("Need at least two numeric columns for a scatter plot.")
        else:
            xcol = st.selectbox("X", num_cols, index=0)
            ycol = st.selectbox("Y", num_cols, index=1)
            fig3, ax3 = plt.subplots()
            sns.scatterplot(x=data[xcol], y=data[ycol], ax=ax3)
            ax3.set_xlabel(xcol)
            ax3.set_ylabel(ycol)
            st.pyplot(fig3)

    # KPI by Category (defaults to customer_segment if present)
    st.divider()
    st.subheader("KPI by Category")
    seg_choices = candidate_categoricals(merged, extra=["customer_segment", "segment", "tier", "region"], max_uniques=50)
    if seg_choices and tx_rev in data.columns:
        default_idx = 0
        for pref in ["customer_segment", "segment", "tier", "region"]:
            if pref in seg_choices:
                default_idx = seg_choices.index(pref)
                break
        seg_col = st.selectbox("Category column", seg_choices, index=default_idx)
        seg = (
            data.groupby(seg_col, dropna=False)[tx_rev]
            .agg(total_revenue="sum", transactions="size", aov=lambda s: s.sum() / len(s))
            .reset_index()
            .sort_values("total_revenue", ascending=False)
        )
        st.dataframe(seg, use_container_width=True)
    else:
        st.caption("Upload customers.csv (and/or choose a different revenue column) to enable KPI by category.")

    # Preview
    with st.expander("Preview merged data"):
        st.dataframe(data.head(50), use_container_width=True)

# Guard — never silently blank-screen
try:
    main()
except Exception:
    st.error("Unexpected error (details below).")
    st.code(traceback.format_exc(), language="python")
