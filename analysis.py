"""
EPA Air Quality Index Analysis — Bedrock Job Definition
=======================================================
Queries the EPA AQI Iceberg dataset through the Bedrock query engine
(ABAC enforced), materialises summary Parquet files for the Bedrock Dash
dashboard, and emits structured progress events visible in the Bedrock UI.
"""

import os
import sys

sys.path.insert(0, "/")
from bedrock_sdk import BedrockJob

job = BedrockJob()
conn = job.connect()

year = int(os.environ.get("PARAM_YEAR", 2023))

# ── 1. Fetch data from Iceberg (ABAC enforced via query engine) ──────────────
job.update_progress("running_analysis", progress_pct=5,
                    progress_message="Connecting to query engine…")

job.fetch("aqi_daily", f"""
    SELECT defining_parameter, aqi, category, county_name, state_name, date, year
    FROM bedrock.environment.epa_aqi_daily
    WHERE year = {year}
""")

job.update_progress("running_analysis", progress_pct=10,
                    progress_message=f"Analysing {year} AQI data…")

# ── 2. Monthly AQI trend ─────────────────────────────────────────────────────
job.progress(25, "Monthly trends computed")

# ── 3. Category breakdown ────────────────────────────────────────────────────
job.progress(40, "Category breakdown done")

# ── 4. Pollutant analysis ────────────────────────────────────────────────────
job.progress(55, "Pollutant analysis done")

# ── 5. Hotspot analysis ──────────────────────────────────────────────────────
job.progress(70, "Hotspot analysis done")

# ── 6. State summary ─────────────────────────────────────────────────────────
job.progress(85, "State summary done")

# ── 7. Write Parquet files via presigned URLs (no R2 creds needed) ────────────
job.progress(90, "Writing parquet files…")

job.write_parquet("monthly_trend", f"""
    SELECT
        CAST(DATE_TRUNC('month', date::DATE) AS VARCHAR) AS month,
        ROUND(AVG(aqi), 1)  AS avg_aqi,
        MAX(aqi)            AS max_aqi,
        COUNT(*)            AS readings
    FROM aqi_daily
    GROUP BY month
    ORDER BY month
""")

job.write_parquet("categories", """
    SELECT
        category,
        COUNT(*)                                            AS days,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM aqi_daily
    GROUP BY category
    ORDER BY days DESC
""")

job.write_parquet("pollutants", """
    SELECT
        defining_parameter AS pollutant,
        COUNT(*)           AS days,
        ROUND(AVG(aqi), 1) AS avg_aqi,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM aqi_daily
    GROUP BY defining_parameter
    ORDER BY days DESC
""")

job.write_parquet("hotspots", """
    SELECT
        state_name,
        county_name,
        COUNT(*) FILTER (WHERE category NOT IN ('Good', 'Moderate')) AS unhealthy_days,
        ROUND(AVG(aqi), 1) AS avg_aqi,
        MAX(aqi)            AS max_aqi
    FROM aqi_daily
    GROUP BY state_name, county_name
    HAVING COUNT(*) FILTER (WHERE category NOT IN ('Good', 'Moderate')) > 0
    ORDER BY unhealthy_days DESC
    LIMIT 30
""")

job.write_parquet("states", """
    SELECT
        state_name,
        COUNT(*)            AS readings,
        ROUND(AVG(aqi), 1) AS avg_aqi,
        MAX(aqi)            AS max_aqi,
        COUNT(*) FILTER (WHERE category = 'Good') AS good_days,
        COUNT(*) FILTER (WHERE category != 'Good') AS not_good_days
    FROM aqi_daily
    GROUP BY state_name
    ORDER BY state_name
""")

# ── 8. Emit structured report ────────────────────────────────────────────────
out_prefix = f"analytics/bedrock/{job.job_id}/data"
job.update_progress("running_analysis", progress_pct=95,
                    progress_message="Finalising report…",
                    lineage={
                        "inputs":  ["bedrock.environment.epa_aqi_daily"],
                        "outputs": [f"{out_prefix}/monthly_trend.parquet",
                                    f"{out_prefix}/categories.parquet",
                                    f"{out_prefix}/pollutants.parquet",
                                    f"{out_prefix}/hotspots.parquet",
                                    f"{out_prefix}/states.parquet"]
                    })

categories = conn.execute("""
    SELECT category, COUNT(*) AS days,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM aqi_daily GROUP BY category ORDER BY days DESC
""").fetchall()

pollutants = conn.execute("""
    SELECT defining_parameter, COUNT(*) AS days,
           ROUND(AVG(aqi), 1) AS avg_aqi,
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) AS pct
    FROM aqi_daily GROUP BY defining_parameter ORDER BY days DESC
""").fetchall()

job.table(
    id="category_summary",
    title=f"AQI Category Distribution ({year})",
    headers=["Category", "Days", "%"],
    rows=[[r[0], f"{r[1]:,}", r[2]] for r in categories],
)

job.table(
    id="pollutant_summary",
    title=f"Defining Pollutants ({year})",
    headers=["Pollutant", "Days", "Avg AQI", "%"],
    rows=[[r[0], f"{r[1]:,}", r[2], r[3]] for r in pollutants],
)

job.write_dashboard("dashboard/index.md")

job.complete()
