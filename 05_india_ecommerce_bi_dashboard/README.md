# India E-commerce Business Intelligence Dashboard

## Goal
Create an executive BI layer over Project 01's synthetic Indian retail case dataset. The Power BI and Tableau imports reconcile to the same 18,000-row source table.

## Interactive dashboard
Run `streamlit run app.py` from the repository root. The fifth page is the e-commerce BI dashboard; the same app also exposes the four analytical project dashboards. A standalone Plotly gallery is available at `dashboard_previews/index.html`.

## Power BI
- Import `data/processed/powerbi_table_orders.csv`.
- Use `powerbi/DAX_MEASURES.dax` and `powerbi/BUILD_GUIDE.md`.
- Save a native `.pbix` from Power BI Desktop after validating visuals.

## Tableau
- Connect to the same CSV.
- Follow `tableau/BUILD_GUIDE.md` and save a native `.twb/.twbx` from Tableau Desktop/Public.

## Data disclosure
The underlying order-level data are synthetic and do not represent actual Indian marketplace transactions. Native Power BI/Tableau workbook files are not bundled; import-ready data, DAX, and build instructions are included.

## Updated BI page scope
The fifth Streamlit page is intentionally distinct from the Project 01 analyst workflow. It is organized into three reporting tabs:
- **Executive overview:** sales trend, category mix and executive takeaway.
- **Customer & product mix:** one-time/repeat customer split, sales by customer type and payment method.
- **Operations & fulfilment:** order-status mix, late/on-time delivery volumes and cancellation context.

The page uses the same synthetic Project 01 source table. It demonstrates a separate BI reporting perspective, not a new independent dataset. Filters apply across the page and the filtered rows can be exported.
