---
title: EPA Air Quality Index
sidebar_position: 1
---

```sql monthly_trend
SELECT month::DATE AS month,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi,
       readings::BIGINT AS readings
FROM results.monthly_trend ORDER BY month
```

```sql categories
SELECT REPLACE(category, '"', '') AS category,
       days::BIGINT AS days,
       pct::DOUBLE AS pct
FROM results.categories ORDER BY pct DESC
```

```sql pollutants
SELECT REPLACE(pollutant, '"', '') AS pollutant,
       days::BIGINT AS days,
       avg_aqi::DOUBLE AS avg_aqi,
       pct::DOUBLE AS pct
FROM results.pollutants ORDER BY days DESC
```

```sql hotspots
SELECT REPLACE(state_name, '"', '') AS state_name,
       REPLACE(county_name, '"', '') AS county_name,
       unhealthy_days::INT AS unhealthy_days,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi
FROM results.hotspots ORDER BY unhealthy_days DESC
```

```sql states
SELECT REPLACE(state_name, '"', '') AS state_name,
       readings::BIGINT AS readings,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi,
       good_days::BIGINT AS good_days,
       not_good_days::BIGINT AS not_good_days
FROM results.states ORDER BY avg_aqi DESC
```

```sql summary
SELECT ROUND(AVG(avg_aqi::DOUBLE), 1) AS national_avg_aqi,
       MAX(max_aqi::INT) AS peak_aqi,
       SUM(readings::BIGINT) AS total_readings
FROM results.monthly_trend
```

```sql unhealthy_total
SELECT SUM(unhealthy_days::INT) AS total_unhealthy_days
FROM results.hotspots
```

```sql good_pct
SELECT ROUND(SUM(CASE WHEN REPLACE(category, '"', '') = 'Good' THEN pct::DOUBLE ELSE 0 END), 1) AS good_pct
FROM results.categories
```

```sql hotspots_filtered
SELECT state_name, county_name, unhealthy_days, avg_aqi, max_aqi
FROM (
  SELECT REPLACE(state_name, '"', '') AS state_name,
         REPLACE(county_name, '"', '') AS county_name,
         unhealthy_days::INT AS unhealthy_days,
         avg_aqi::DOUBLE AS avg_aqi,
         max_aqi::INT AS max_aqi
  FROM results.hotspots
)
WHERE unhealthy_days >= COALESCE(NULLIF('${inputs.min_unhealthy_days}','')::INT, 20)
ORDER BY unhealthy_days DESC
```

```sql states_filtered
SELECT state_name, readings, avg_aqi, max_aqi, good_days, not_good_days
FROM (
  SELECT REPLACE(state_name, '"', '') AS state_name,
         readings::BIGINT AS readings,
         avg_aqi::DOUBLE AS avg_aqi,
         max_aqi::INT AS max_aqi,
         good_days::BIGINT AS good_days,
         not_good_days::BIGINT AS not_good_days
  FROM results.states
)
WHERE avg_aqi >= COALESCE(NULLIF('${inputs.min_aqi}','')::DOUBLE, 30)
ORDER BY avg_aqi DESC
```

```sql pollutant_detail
SELECT REPLACE(pollutant, '"', '') AS pollutant,
       days::BIGINT AS days,
       avg_aqi::DOUBLE AS avg_aqi,
       pct::DOUBLE AS pct
FROM results.pollutants
WHERE REPLACE(pollutant, '"', '') = '${inputs.selected_pollutant}'
   OR '${inputs.selected_pollutant}' = 'All'
ORDER BY days DESC
```

<BigValue data={summary} value="national_avg_aqi" title="National Avg AQI" />
<BigValue data={summary} value="peak_aqi" title="Peak AQI Reading" />
<BigValue data={summary} value="total_readings" title="Total Readings" fmt="num0" />
<BigValue data={good_pct} value="good_pct" title="Good Air Days" fmt="num1" suffix="%" />

## Monthly AQI Trend

<Grid cols=2>
  <AreaChart
    data={monthly_trend}
    x="month"
    y="avg_aqi"
    title="Average AQI by Month"
    yAxisTitle="AQI"
    colorPalette={["#10B981"]}
  />
  <BarChart
    data={monthly_trend}
    x="month"
    y="max_aqi"
    title="Peak AQI by Month"
    yAxisTitle="Max AQI"
    colorPalette={["#EF4444"]}
  />
</Grid>

## Air Quality Categories & Pollutants

<Grid cols=2>
  <BarChart
    data={categories}
    x="category"
    y="days"
    title="Days by AQI Category"
    colorPalette={["#10B981","#F59E0B","#F97316","#EF4444","#7C3AED","#991B1B"]}
  />
  <BarChart
    data={pollutants}
    x="pollutant"
    y="days"
    title="Days by Defining Pollutant"
    colorPalette={["#3B82F6"]}
  />
</Grid>

<Grid cols=2>
  <DataTable data={categories}>
    <Column id="category" title="Category" />
    <Column id="days" title="Days" fmt="num0" />
    <Column id="pct" title="% of Total" fmt="num1" suffix="%" />
  </DataTable>
  <DataTable data={pollutants}>
    <Column id="pollutant" title="Pollutant" />
    <Column id="days" title="Days" fmt="num0" />
    <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
    <Column id="pct" title="% of Total" fmt="num1" suffix="%" />
  </DataTable>
</Grid>

## Unhealthy Day Hotspots

<Slider name="min_unhealthy_days" title="Minimum Unhealthy Days" min=5 max=100 step=5 defaultValue=20 />

<Grid cols=2>
  <BarChart
    data={hotspots_filtered}
    x="county_name"
    y="unhealthy_days"
    title="Counties by Unhealthy Days"
    colorPalette={["#EF4444"]}
    xTickMarks=true
  />
  <DataTable data={hotspots_filtered} rows=15>
    <Column id="state_name" title="State" />
    <Column id="county_name" title="County" />
    <Column id="unhealthy_days" title="Unhealthy Days" fmt="num0" />
    <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
    <Column id="max_aqi" title="Peak AQI" />
  </DataTable>
</Grid>

[View all states →](/states)

## State Comparison

<Slider name="min_aqi" title="Minimum Avg AQI" min=20 max=60 step=1 defaultValue=30 />

<Grid cols=2>
  <BarChart
    data={states_filtered}
    x="state_name"
    y="avg_aqi"
    title="States by Average AQI"
    colorPalette={["#F59E0B"]}
    xTickMarks=true
  />
  <DataTable data={states_filtered} rows=20>
    <Column id="state_name" title="State" />
    <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
    <Column id="max_aqi" title="Peak AQI" />
    <Column id="good_days" title="Good Days" fmt="num0" />
    <Column id="not_good_days" title="Not Good" fmt="num0" />
  </DataTable>
</Grid>
