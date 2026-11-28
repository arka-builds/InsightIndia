# SQLite database

Run from repository root:

```bash
python database/build_database.py
```

This creates `database/insightindia_analytics.sqlite` with four tables. The database is reproducible from the CSVs; it is safe to delete and rebuild. Run queries in `queries.sql` using DB Browser for SQLite or the `sqlite3` CLI.

Data provenance is carried in project-level source registers. E-commerce and A/B test tables are synthetic; MoRTH and RBI tables are official-source extracts.
