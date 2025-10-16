# TJX EIC Workspace

This repository contains notebooks, data, and example apps used across the TJX EIC case studies and demos. Use this README to understand the layout and how to set up your local environment.

## Environment setup

- Make a copy of `.env.copy` at the repo root, rename it to `.env`, and update the values for your environment.
	- This is used by notebooks and utilities that rely on environment variables (for example, Snowflake connection settings like SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, etc.).
	- Keep `.env` out of source control (it should be ignored by default). Do not commit secrets.

## Folder and file overview

Below is a high-level map of the repository. The table after this tree lists each file/folder with a short description.

```
./
├─ README.md
├─ __pycache__/
├─ ai-shopper/
│  ├─ README.md
│  ├─ requirements.txt
│  ├─ tjmaxx_catalog.json
│  ├─ fixtures/
│  │  └─ sample_product_1.html
│  ├─ tests/
│  │  └─ test_basic.py
│  └─ tjx_style_demo/
│     ├─ __init__.py
│     ├─ catalog.py
│     ├─ config.py
│     ├─ llm.py
│     ├─ main.py
│     ├─ quiz.py
│     └─ streamlit_app.py
├─ case-study/
│  ├─ cav_analysis.ipynb
│  ├─ cp_analysis.ipynb
│  ├─ oe_analysis.ipynb
│  ├─ data/
│  │  ├─ customer_touchpoints_v2.csv
│  │  ├─ customer_touchpoints.csv
│  │  ├─ customers_no_header.csv
│  │  ├─ customers.csv
│  │  ├─ inventory_snapshots.csv
│  │  ├─ marketing_campaigns_no_header.csv
│  │  ├─ marketing_campaigns.csv
│  │  ├─ marketing_spend.csv
│  │  ├─ products.csv
│  │  ├─ stores.csv
│  │  ├─ transaction_items_v2.csv
│  │  ├─ transaction_items.csv
│  │  ├─ transactions_v2.csv
│  │  └─ transactions.csv
│  └─ students/
│     ├─ cav_analysis.ipynb
│     ├─ cp_analysis.ipynb
│     └─ oe_analysis.ipynb
├─ notebooks/
│  ├─ cx_analysis.ipynb
│  ├─ python-basics.ipynb
│  ├─ python-ingest.ipynb
│  ├─ python-snowflake.ipynb
│  ├─ snowflake-customers-crud.ipynb
│  ├─ sqlite-customers-crud.ipynb
│  └─ test.ipynb
├─ parquet_orders_jan/
├─ parquet_orders_schema/
├─ streamlit/
│  ├─ app1.py
│  ├─ app2.py
│  ├─ app3.py
│  └─ app4.py
└─ tests/
	 ├─ cart.py
	 ├─ math_utils.py
	 ├─ math_utils_test.py
	 └─ test_cart.py
```

### Files and folders reference

| Path | Type | Description |
|------|------|-------------|
| `README.md` | File | Root documentation for the repository and setup instructions. |
| `__pycache__/` | Folder | Python bytecode caches (auto-generated). |
| `ai-shopper/` | Folder | Demo code for an AI-assisted shopping/style app. |
| `ai-shopper/README.md` | File | Documentation specific to the AI shopper demo. |
| `ai-shopper/requirements.txt` | File | Python dependencies for the AI shopper demo. |
| `ai-shopper/tjmaxx_catalog.json` | File | Sample product catalog JSON used by the demo. |
| `ai-shopper/fixtures/` | Folder | Static fixture data for tests and examples. |
| `ai-shopper/fixtures/sample_product_1.html` | File | Example product HTML fixture. |
| `ai-shopper/tests/` | Folder | Unit tests for the AI shopper demo. |
| `ai-shopper/tests/test_basic.py` | File | Basic test case for demo functionality. |
| `ai-shopper/tjx_style_demo/` | Folder | Core package for the style demo. |
| `ai-shopper/tjx_style_demo/__init__.py` | File | Package initializer. |
| `ai-shopper/tjx_style_demo/catalog.py` | File | Catalog utilities for the style demo. |
| `ai-shopper/tjx_style_demo/config.py` | File | Configuration helpers for the style demo. |
| `ai-shopper/tjx_style_demo/llm.py` | File | LLM integration helpers for the demo. |
| `ai-shopper/tjx_style_demo/main.py` | File | Entrypoint script(s) for running the demo. |
| `ai-shopper/tjx_style_demo/quiz.py` | File | Quiz/interaction logic for the demo. |
| `ai-shopper/tjx_style_demo/streamlit_app.py` | File | Streamlit app for the style demo UI. |
| `case-study/` | Folder | Case study notebooks and datasets. |
| `case-study/cav_analysis.ipynb` | File | Case study notebook: CAV analysis. |
| `case-study/cp_analysis.ipynb` | File | Case study notebook: CP analysis. |
| `case-study/oe_analysis.ipynb` | File | Case study notebook: OE analysis. |
| `case-study/data/` | Folder | CSV datasets used by case study notebooks. |
| `case-study/data/customer_touchpoints_v2.csv` | File | Customer touchpoints dataset (v2). |
| `case-study/data/customer_touchpoints.csv` | File | Customer touchpoints dataset. |
| `case-study/data/customers_no_header.csv` | File | Customers dataset without header. |
| `case-study/data/customers.csv` | File | Customers dataset. |
| `case-study/data/inventory_snapshots.csv` | File | Inventory snapshots dataset. |
| `case-study/data/marketing_campaigns_no_header.csv` | File | Marketing campaigns dataset without header. |
| `case-study/data/marketing_campaigns.csv` | File | Marketing campaigns dataset. |
| `case-study/data/marketing_spend.csv` | File | Marketing spend dataset. |
| `case-study/data/products.csv` | File | Products dataset. |
| `case-study/data/stores.csv` | File | Stores dataset. |
| `case-study/data/transaction_items_v2.csv` | File | Transaction items dataset (v2). |
| `case-study/data/transaction_items.csv` | File | Transaction items dataset. |
| `case-study/data/transactions_v2.csv` | File | Transactions dataset (v2). |
| `case-study/data/transactions.csv` | File | Transactions dataset. |
| `case-study/students/` | Folder | Student-facing copies of case study notebooks. |
| `case-study/students/cav_analysis.ipynb` | File | Student notebook: CAV analysis. |
| `case-study/students/cp_analysis.ipynb` | File | Student notebook: CP analysis. |
| `case-study/students/oe_analysis.ipynb` | File | Student notebook: OE analysis. |
| `notebooks/` | Folder | General notebooks for data, Snowflake, and CRUD examples. |
| `notebooks/cx_analysis.ipynb` | File | Customer experience analysis notebook. |
| `notebooks/python-basics.ipynb` | File | Python basics notebook. |
| `notebooks/python-ingest.ipynb` | File | Data ingestion examples notebook. |
| `notebooks/python-snowflake.ipynb` | File | Snowflake exploration notebook (DataFrame, batching, Parquet, etc.). |
| `notebooks/snowflake-customers-crud.ipynb` | File | Snowflake CRUD demo notebook (connect via env vars). |
| `notebooks/sqlite-customers-crud.ipynb` | File | SQLite CRUD demo notebook. |
| `notebooks/test.ipynb` | File | Scratch/test notebook. |
| `parquet_orders_jan/` | Folder | Example output directory for Parquet exports (January slice). |
| `parquet_orders_schema/` | Folder | Example output directory for Parquet exports with fixed schema. |
| `streamlit/` | Folder | Streamlit mini apps for demos. |
| `streamlit/app1.py` | File | Streamlit app example 1. |
| `streamlit/app2.py` | File | Streamlit app example 2. |
| `streamlit/app3.py` | File | Streamlit app example 3. |
| `streamlit/app4.py` | File | Streamlit app example 4. |
| `tests/` | Folder | Simple Python modules and tests used in examples. |
| `tests/cart.py` | File | Cart implementation used in tests. |
| `tests/math_utils.py` | File | Math utilities module. |
| `tests/math_utils_test.py` | File | Tests for math utilities. |
| `tests/test_cart.py` | File | Tests for cart module. |

## Quick start

1) Create and populate your environment file

```
cp .env.copy .env
# then open .env and fill in your values
```

2) (Optional) Create a virtual environment and install demo dependencies

```
python3 -m venv .venv
source .venv/bin/activate
pip install -r ai-shopper/requirements.txt
```

3) Open notebooks from the `notebooks/` or `case-study/` folders in VS Code or Jupyter and run cells as needed. Some notebooks will pip-install their own small dependencies inside the first cell.

4) To run Streamlit demos, use the files in `ai-shopper/tjx_style_demo/streamlit_app.py` or the apps in `streamlit/` (these may require additional packages depending on your environment).
