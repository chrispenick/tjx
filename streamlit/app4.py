# app_snowflake.py
# Streamlit <-> Snowflake: connector (SQL+pandas) + optional Snowpark in one app.

import time
import traceback
from typing import Optional, Dict

import pandas as pd
import streamlit as st

# Try to import both client libraries gracefully
try:
    import snowflake.connector as sf
    HAVE_CONNECTOR = True
except Exception:
    HAVE_CONNECTOR = False

# try:
#     from snowflake.snowpark import Session as SnowparkSession
#     HAVE_SNOWPARK = True
# except Exception:
#     HAVE_SNOWPARK = False

# =========================
# Page setup
# =========================
st.set_page_config(page_title="Streamlit ↔ Snowflake", layout="wide")
st.set_option("client.showErrorDetails", True)
st.title("Streamlit ↔ Snowflake")

st.caption(
    "Demo: connect with the Snowflake Python Connector (SQL → pandas), "
    "and optionally via Snowpark (Session → DataFrame)."
)

# =========================
# Helpers: Credentials & Config
# =========================
def read_secrets_block() -> Dict[str, str]:
    """Read st.secrets['snowflake'] if present, otherwise return empty dict."""
    try:
        return dict(st.secrets.get("snowflake", {}))
    except Exception:
        return {}

def build_conn_dict_from_ui(defaults: Dict[str, str]) -> Dict[str, str]:
    """Render connection inputs; fill from secrets if available."""
    with st.sidebar:
        st.header("Connection")
        account   = st.text_input("Account",   value=defaults.get("account", ""), placeholder="xy12345.us-west-2")
        user      = st.text_input("User",      value=defaults.get("user", ""))   # don't echo password here
        password  = st.text_input("Password",  value=defaults.get("password", ""), type="password")
        role      = st.text_input("Role",      value=defaults.get("role", "SYSADMIN"))
        warehouse = st.text_input("Warehouse", value=defaults.get("warehouse", "COMPUTE_WH"))
        database  = st.text_input("Database",  value=defaults.get("database", "DEMO_DB"))
        schema    = st.text_input("Schema",    value=defaults.get("schema", "PUBLIC"))

        st.caption("Tip: configure `.streamlit/secrets.toml` so you don't enter these every time.")
    return {
        "account": account.strip(),
        "user": user.strip(),
        "password": password,
        "role": role.strip(),
        "warehouse": warehouse.strip(),
        "database": database.strip(),
        "schema": schema.strip(),
    }

def is_complete(cfg: Dict[str, str]) -> bool:
    required = ["account", "user", "password", "warehouse", "database", "schema"]
    return all(cfg.get(k) for k in required)

# =========================
# Connector (SQL + pandas)
# =========================
def connector_connect(cfg: Dict[str, str]):
    """Create a Snowflake connection via snowflake-connector-python."""
    if not HAVE_CONNECTOR:
        raise RuntimeError("snowflake-connector-python is not installed. `pip install snowflake-connector-python`")
    return sf.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        role=cfg.get("role"),
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        client_session_keep_alive=True,
    )

@st.cache_data(show_spinner=False, ttl=60)
def run_sql_cached(cfg: Dict[str, str], sql: str) -> pd.DataFrame:
    """Run SQL and return pandas DataFrame (cached)."""
    con = connector_connect(cfg)
    try:
        df = pd.read_sql(sql, con)
    finally:
        con.close()
    return df

def run_sql_live(cfg: Dict[str, str], sql: str) -> pd.DataFrame:
    """Run SQL without cache (for ad-hoc)."""
    con = connector_connect(cfg)
    try:
        df = pd.read_sql(sql, con)
    finally:
        con.close()
    return df

def connector_info(cfg: Dict[str, str]) -> pd.DataFrame:
    """Return core session info via connector."""
    q = """
    SELECT
      CURRENT_VERSION()               AS SF_VERSION,
      CURRENT_ACCOUNT()               AS ACCOUNT,
      CURRENT_REGION()                AS REGION,
      CURRENT_ROLE()                  AS ROLE,
      CURRENT_WAREHOUSE()             AS WAREHOUSE,
      CURRENT_DATABASE()              AS DATABASE,
      CURRENT_SCHEMA()                AS SCHEMA
    """
    return run_sql_live(cfg, q)

# =========================
# Snowpark (optional)
# =========================
# def snowpark_session(cfg: Dict[str, str]):
#     if not HAVE_SNOWPARK:
#         raise RuntimeError("snowflake-snowpark-python is not installed. `pip install snowflake-snowpark-python`")
#     sp_cfg = {
#         "account": cfg["account"],
#         "user": cfg["user"],
#         "password": cfg["password"],
#         "role": cfg.get("role"),
#         "warehouse": cfg["warehouse"],
#         "database": cfg["database"],
#         "schema": cfg["schema"],
#     }
#     return SnowparkSession.builder.configs(sp_cfg).create()

# =========================
# UI: Connect & Mode
# =========================
secrets_cfg = read_secrets_block()
conn_cfg = build_conn_dict_from_ui(secrets_cfg)

colA, colB, colC = st.columns([1.5, 1, 1])
with colA:
    mode = st.radio("Client Library", ["Connector (SQL + pandas)", "Snowpark (optional)"], horizontal=True)
with colB:
    test_btn = st.button("Test connection")
with colC:
    clear_cache = st.button("Clear cache")

if clear_cache:
    st.cache_data.clear()
    st.success("Cache cleared.")

if not is_complete(conn_cfg):
    st.warning("Enter your Snowflake credentials in the sidebar (or configure `.streamlit/secrets.toml`).")
    st.stop()

# =========================
# Connection Test
# =========================
if test_btn:
    try:
        if mode.startswith("Connector"):
            info = connector_info(conn_cfg)
        else:
            # Snowpark test
            s = snowpark_session(conn_cfg)
            info = s.sql("""
                SELECT CURRENT_VERSION() AS SF_VERSION,
                       CURRENT_ACCOUNT()  AS ACCOUNT,
                       CURRENT_REGION()   AS REGION,
                       CURRENT_ROLE()     AS ROLE,
                       CURRENT_WAREHOUSE() AS WAREHOUSE,
                       CURRENT_DATABASE()  AS DATABASE,
                       CURRENT_SCHEMA()    AS SCHEMA
            """).to_pandas()
            s.close()
        st.success("Connected!")
        st.dataframe(info, use_container_width=True)
    except Exception as e:
        st.error("Connection failed.")
        st.code(traceback.format_exc(), language="python")

st.divider()

# =========================
# Schema Browser (Connector)
# =========================
st.subheader("Schema Browser (Connector)")
if not HAVE_CONNECTOR:
    st.info("Install `snowflake-connector-python` to use the schema browser.")
else:
    # Lists for DB/SCHEMA/TABLE selection
    try:
        dbs = run_sql_cached(conn_cfg, "SHOW DATABASES").sort_values("name", key=lambda s: s.str.lower())
        db = st.selectbox("Database", dbs["name"].tolist(), index=max(dbs.index[dbs["name"].str.upper()==conn_cfg["database"].upper()].tolist()+[0]))
        schemas = run_sql_cached(conn_cfg, f"SHOW SCHEMAS IN DATABASE {db}")
        schema = st.selectbox("Schema", schemas["name"].tolist(), index=max(schemas.index[schemas["name"].str.upper()==conn_cfg["schema"].upper()].tolist()+[0]))
        tables = run_sql_cached(conn_cfg, f"SHOW TABLES IN {db}.{schema}")
        table = st.selectbox("Table", tables["name"].tolist() if not tables.empty else ["(none)"])
        preview_btn = st.button("Preview table", type="primary")
        if preview_btn and table and table != "(none)":
            t0 = time.time()
            df = run_sql_live(conn_cfg, f'SELECT * FROM "{db}"."{schema}"."{table}" LIMIT 500')
            dur = time.time() - t0
            st.caption(f"Fetched {len(df):,} rows in {dur:.2f}s")
            st.dataframe(df, use_container_width=True)
            st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8"), file_name=f"{db}_{schema}_{table}.csv", mime="text/csv")
    except Exception as e:
        st.error("Schema browser error.")
        st.code(traceback.format_exc(), language="python")

st.divider()

# =========================
# Ad-hoc Query Runner
# =========================
st.subheader("Ad-hoc SQL (Connector or Snowpark)")

default_sql = (
    f'SELECT CURRENT_DATE() AS TODAY, COUNT(*) AS TABLES '
    f'FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = \'{conn_cfg["schema"].upper()}\';'
)

sql = st.text_area("SQL", value=default_sql, height=150, help="Write any read-only SQL. Avoid DDL/DML in demos.")
run_cached = st.checkbox("Cache this query (60s)", value=False)
run_btn = st.button("Run query")

if run_btn and sql.strip():
    try:
        t0 = time.time()
        if mode.startswith("Connector"):
            df = run_sql_cached(conn_cfg, sql) if run_cached else run_sql_live(conn_cfg, sql)
        else:
            s = snowpark_session(conn_cfg)
            df = s.sql(sql).to_pandas()
            s.close()
        dur = time.time() - t0
        st.caption(f"Returned {len(df):,} rows in {dur:.2f}s")
        st.dataframe(df, use_container_width=True)
        st.download_button("Download CSV", data=df.to_csv(index=False).encode("utf-8"), file_name="query_results.csv", mime="text/csv")
    except Exception:
        st.error("Query failed.")
        st.code(traceback.format_exc(), language="python")

st.divider()

# =========================
# Quick How-To / Notes
# =========================
with st.expander("How this works / Tips"):
    st.markdown("""
- **Connector (SQL + pandas)** uses `snowflake-connector-python` to create a connection and `pandas.read_sql` to fetch results.
- **Snowpark** uses `snowflake-snowpark-python` to create a `Session`, then `session.sql(...).to_pandas()`.

**Security**
- Store credentials in `.streamlit/secrets.toml` under `[snowflake]`.
- Avoid checking secrets into source control.
- In production, consider OAuth or key-pair auth (instead of password).

**Performance**
- Use `st.cache_data(ttl=60)` for stable, repeated queries (schema lists, small lookups).
- For large tables, filter in SQL (`WHERE`, `LIMIT`) before bringing into pandas.

**Common gotchas**
- `account` should include region (e.g., `xy12345.us-west-2`), **not** the full URL.
- Make sure `role`, `warehouse`, `database`, `schema` exist and you have usage grants.
- If Snowpark is not installed, the UI falls back to Connector mode.
""")
