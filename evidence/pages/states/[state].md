---
title: ${params.state} — Air Quality
---

```sql state_monthly
SELECT REPLACE(month, '"', '')::DATE AS month,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi,
       readings::BIGINT AS readings
FROM results.monthly_trend ORDER BY month
```

```sql state_summary
SELECT REPLACE(state_name, '"', '') AS state_name,
       readings::BIGINT AS readings,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi,
       good_days::BIGINT AS good_days,
       not_good_days::BIGINT AS not_good_days
FROM results.states
WHERE REPLACE(state_name, '"', '') = '${params.state}'
```

```sql state_hotspots
SELECT REPLACE(state_name, '"', '') AS state_name,
       REPLACE(county_name, '"', '') AS county_name,
       unhealthy_days::INT AS unhealthy_days,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi
FROM results.hotspots
WHERE REPLACE(state_name, '"', '') = '${params.state}'
ORDER BY unhealthy_days DESC
```

```sql all_states
SELECT REPLACE(state_name, '"', '') AS state_name,
       avg_aqi::DOUBLE AS avg_aqi,
       '/states/' || REPLACE(REPLACE(state_name, '"', ''), ' ', '%20') AS state_link
FROM results.states
ORDER BY state_name
```

# {params.state}

<BigValue data={state_summary} value="avg_aqi" title="Average AQI" fmt="num1" />
<BigValue data={state_summary} value="max_aqi" title="Peak AQI" />
<BigValue data={state_summary} value="readings" title="Total Readings" fmt="num0" />
<BigValue data={state_summary} value="good_days" title="Good Days" fmt="num0" />

## Monthly Trend

<Grid cols=2>
  <AreaChart
    data={state_monthly}
    x="month"
    y="avg_aqi"
    title="Average AQI by Month"
    yAxisTitle="AQI"
    colorPalette={["#10B981"]}
  />
  <BarChart
    data={state_monthly}
    x="month"
    y="max_aqi"
    title="Peak AQI by Month"
    yAxisTitle="Max AQI"
    colorPalette={["#EF4444"]}
  />
</Grid>

## County Hotspots

<DataTable data={state_hotspots}>
  <Column id="county_name" title="County" />
  <Column id="unhealthy_days" title="Unhealthy Days" fmt="num0" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
  <Column id="max_aqi" title="Peak AQI" />
</DataTable>

## All States

<DataTable data={all_states} search=true link="state_link" rows=10>
  <Column id="state_name" title="State" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
</DataTable>
