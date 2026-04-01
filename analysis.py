"""
EPA Air Quality Index Analysis — Bedrock Job Definition
========================================================
Queries the EPA AQI daily Iceberg dataset, computes summary statistics,
and writes Parquet output for the Evidence dashboard.
"""

import os
import sys

sys.path.insert(0, "/")
from bedrock_sdk import BedrockJob

job = BedrockJob()

# ── 1. Connect via Arrow Flight (ABAC enforced by the query engine) ───────────
job.update_progress("running_analysis", progress_pct=5,
                    progress_message="Connecting to query engine…")
conn = job.connect()

year = int(os.environ.get("PARAM_YEAR", 2023))
state_filter = os.environ.get("PARAM_STATE", "").strip()

where = f"WHERE year = {year}"
if state_filter:
    where += f" AND state_name = '{state_filter}'"

job.update_progress("running_analysis", progress_pct=10,
                    progress_message=f"Analysing {year} AQI data…")

# ── 2. Monthly AQI trend ──────────────────────────────────────────────────────
monthly = conn.execute(f"""
    SELECT DATE_TRUNC('month', date::DATE)::DATE AS month,
           ROUND(AVG(aqi), 1) AS avg_aqi,
           MAX(aqi) AS max_aqi,
           COUNT(*) AS readings
    FROM catalog.environment.epa_aqi_daily
    {where}
    GROUP BY month ORDER BY month
""").fetchall()
job.progress(25, "Monthly trends computed")

# ── 3. Category distribution ──────────────────────────────────────────────────
categories = conn.execute(f"""
    SELECT category,
           COUNT(*) AS days,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM catalog.environment.epa_aqi_daily
    {where}
    GROUP BY category
    ORDER BY MIN(aqi)
""").fetchall()
job.progress(40, "Category breakdown done")

# ── 4. Pollutant breakdown ────────────────────────────────────────────────────
pollutants = conn.execute(f"""
    SELECT defining_parameter AS pollutant,
           COUNT(*) AS days,
           ROUND(AVG(aqi), 1) AS avg_aqi,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
    FROM catalog.environment.epa_aqi_daily
    {where}
    GROUP BY defining_parameter
    ORDER BY days DESC
""").fetchall()
job.progress(55, "Pollutant analysis done")

# ── 5. Top 30 worst counties (most unhealthy days) ───────────────────────────
hotspots = conn.execute(f"""
    SELECT state_name, county_name,
           COUNT(*) FILTER (WHERE category IN ('Unhealthy for Sensitive Groups','Unhealthy','Very Unhealthy','Hazardous')) AS unhealthy_days,
           ROUND(AVG(aqi), 1) AS avg_aqi,
           MAX(aqi) AS max_aqi
    FROM catalog.environment.epa_aqi_daily
    {where}
    GROUP BY state_name, county_name
    HAVING COUNT(*) FILTER (WHERE category IN ('Unhealthy for Sensitive Groups','Unhealthy','Very Unhealthy','Hazardous')) > 0
    ORDER BY unhealthy_days DESC
    LIMIT 30
""").fetchall()
job.progress(70, "Hotspot analysis done")

# ── 6. State summary ─────────────────────────────────────────────────────────
states = conn.execute(f"""
    SELECT state_name,
           COUNT(*) AS readings,
           ROUND(AVG(aqi), 1) AS avg_aqi,
           MAX(aqi) AS max_aqi,
           COUNT(*) FILTER (WHERE category = 'Good') AS good_days,
           COUNT(*) FILTER (WHERE category != 'Good') AS not_good_days
    FROM catalog.environment.epa_aqi_daily
    {where}
    GROUP BY state_name
    ORDER BY avg_aqi DESC
""").fetchall()
job.progress(85, "State summary done")

# ── 7. Write parquet files ────────────────────────────────────────────────────
import json, datetime, duckdb

out = job.output_path
write_conn = duckdb.connect()
write_conn.execute("INSTALL httpfs; LOAD httpfs;")
write_conn.execute(f"""
    CREATE SECRET r2 (TYPE S3,
        KEY_ID '{os.environ["BEDROCK_R2_ACCESS_KEY"]}',
        SECRET '{os.environ["BEDROCK_R2_SECRET_KEY"]}',
        ENDPOINT '{os.environ["BEDROCK_R2_ACCOUNT_ID"]}.r2.cloudflarestorage.com',
        URL_STYLE 'path', USE_SSL true);
""")

def write_parquet(name, rows, columns):
    def _default(o):
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        raise TypeError(f"Not serializable: {type(o).__name__}")
    col_defs = ", ".join(f"v[{i}] AS {c}" for i, c in enumerate(columns))
    vals = json.dumps(rows, default=_default, ensure_ascii=False)
    write_conn.execute(f"""
        COPY (
            SELECT {col_defs}
            FROM (SELECT unnest({vals!r}::JSON[]) AS v)
        ) TO '{out}/{name}.parquet' (FORMAT PARQUET)
    """)
    print(f"  wrote {name}.parquet ({len(rows)} rows)", flush=True)

job.progress(90, "Writing parquet files…")

write_parquet("monthly_trend",  monthly,    ["month", "avg_aqi", "max_aqi", "readings"])
write_parquet("categories",     categories, ["category", "days", "pct"])
write_parquet("pollutants",     pollutants, ["pollutant", "days", "avg_aqi", "pct"])
write_parquet("hotspots",       hotspots,   ["state_name", "county_name", "unhealthy_days", "avg_aqi", "max_aqi"])
write_parquet("states",         states,     ["state_name", "readings", "avg_aqi", "max_aqi", "good_days", "not_good_days"])

# ── 8. Emit structured report ─────────────────────────────────────────────────
job.update_progress("running_analysis", progress_pct=95,
                    progress_message="Finalising report…",
                    lineage={
                        "inputs": ["bedrock.environment.epa_aqi_daily"],
                        "outputs": [f"{out}/{n}.parquet" for n in
                                    ["monthly_trend","categories","pollutants","hotspots","states"]]
                    })

job.table(
    id="category_summary",
    title=f"AQI Category Distribution ({year})",
    headers=["Category", "Days", "%"],
    rows=[[r[0], f"{r[1]:,}", r[2]] for r in categories])

job.table(
    id="pollutant_summary",
    title=f"Defining Pollutants ({year})",
    headers=["Pollutant", "Days", "Avg AQI", "%"],
    rows=[[r[0], f"{r[1]:,}", r[2], r[3]] for r in pollutants])

job.complete()
