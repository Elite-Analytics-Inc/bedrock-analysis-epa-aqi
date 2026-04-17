---
title: EPA Air Quality Index
---

# EPA Air Quality Index

```sql monthly_trend
SELECT month, avg_aqi, max_aqi, readings FROM monthly_trend ORDER BY month
```

```sql categories
SELECT category, days, pct FROM categories ORDER BY pct DESC
```

```sql pollutants
SELECT pollutant, days, avg_aqi, pct FROM pollutants ORDER BY days DESC
```

```sql hotspots
SELECT state_name, county_name, unhealthy_days, avg_aqi, max_aqi FROM hotspots ORDER BY unhealthy_days DESC
```

```sql states
SELECT state_name, readings, avg_aqi, max_aqi, good_days, not_good_days FROM states ORDER BY avg_aqi DESC
```

```sql summary
SELECT ROUND(AVG(avg_aqi), 1) AS national_avg_aqi, MAX(max_aqi) AS peak_aqi, SUM(readings) AS total_readings
FROM monthly_trend
```

```sql good_pct
SELECT ROUND(SUM(CASE WHEN category = 'Good' THEN pct ELSE 0 END), 1) AS good_pct FROM categories
```

```sql hotspots_filtered
SELECT state_name, county_name, unhealthy_days, avg_aqi, max_aqi
FROM hotspots
WHERE unhealthy_days >= ${inputs.min_unhealthy_days}
ORDER BY unhealthy_days DESC
```

```sql states_filtered
SELECT state_name, readings, avg_aqi, max_aqi, good_days, not_good_days
FROM states
WHERE avg_aqi >= ${inputs.min_aqi}
ORDER BY avg_aqi DESC
```

{% big_value data="$summary" value="national_avg_aqi" title="National Avg AQI" /%}
{% big_value data="$summary" value="peak_aqi" title="Peak AQI Reading" /%}
{% big_value data="$summary" value="total_readings" title="Total Readings" fmt="num0" /%}
{% big_value data="$good_pct" value="good_pct" title="Good Air Days" fmt="num1" suffix="%" /%}

## Monthly AQI Trend

{% grid cols=2 %}

{% area_chart data="$monthly_trend" x="month" y="avg_aqi" title="Average AQI by Month" yAxisTitle="AQI" colors=["#10B981"] /%}

{% bar_chart data="$monthly_trend" x="month" y="max_aqi" title="Peak AQI by Month" yAxisTitle="Max AQI" colors=["#EF4444"] /%}

{% /grid %}

## Air Quality Categories & Pollutants

{% grid cols=2 %}

{% bar_chart data="$categories" x="category" y="days" title="Days by AQI Category" colors=["#10B981","#F59E0B","#F97316","#EF4444","#7C3AED","#991B1B"] /%}

{% bar_chart data="$pollutants" x="pollutant" y="days" title="Days by Defining Pollutant" colors=["#3B82F6"] /%}

{% /grid %}

{% grid cols=2 %}

{% data_table data="$categories" %}
{% column id="category" title="Category" /%}
{% column id="days" title="Days" fmt="num0" /%}
{% column id="pct" title="% of Total" fmt="num1" suffix="%" /%}
{% /data_table %}

{% data_table data="$pollutants" %}
{% column id="pollutant" title="Pollutant" /%}
{% column id="days" title="Days" fmt="num0" /%}
{% column id="avg_aqi" title="Avg AQI" fmt="num1" /%}
{% column id="pct" title="% of Total" fmt="num1" suffix="%" /%}
{% /data_table %}

{% /grid %}

## Unhealthy Day Hotspots

{% slider name="min_unhealthy_days" title="Minimum Unhealthy Days" min=5 max=100 step=5 default=20 /%}

{% grid cols=2 %}

{% bar_chart data="$hotspots_filtered" x="county_name" y="unhealthy_days" title="Counties by Unhealthy Days" colors=["#EF4444"] /%}

{% data_table data="$hotspots_filtered" rows=15 %}
{% column id="state_name" title="State" /%}
{% column id="county_name" title="County" /%}
{% column id="unhealthy_days" title="Unhealthy Days" fmt="num0" /%}
{% column id="avg_aqi" title="Avg AQI" fmt="num1" /%}
{% column id="max_aqi" title="Peak AQI" /%}
{% /data_table %}

{% /grid %}

## State Comparison

{% slider name="min_aqi" title="Minimum Avg AQI" min=20 max=60 step=1 default=30 /%}

{% grid cols=2 %}

{% bar_chart data="$states_filtered" x="state_name" y="avg_aqi" title="States by Average AQI" colors=["#F59E0B"] /%}

{% data_table data="$states_filtered" rows=20 %}
{% column id="state_name" title="State" /%}
{% column id="avg_aqi" title="Avg AQI" fmt="num1" /%}
{% column id="max_aqi" title="Peak AQI" /%}
{% column id="good_days" title="Good Days" fmt="num0" /%}
{% column id="not_good_days" title="Not Good" fmt="num0" /%}
{% /data_table %}

{% /grid %}
