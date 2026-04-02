---
title: ${params.state}
---

```sql state_info
SELECT state_name,
       readings,
       avg_aqi,
       max_aqi,
       good_days,
       not_good_days
FROM results.states
WHERE state_name = '${params.state}'
```

```sql state_hotspots
SELECT state_name, county_name, unhealthy_days, avg_aqi, max_aqi
FROM results.hotspots
WHERE state_name = '${params.state}'
ORDER BY unhealthy_days DESC
```

# {params.state}

<BigValue data={state_info} value="avg_aqi" title="Average AQI" fmt="num1" />
<BigValue data={state_info} value="max_aqi" title="Peak AQI" />
<BigValue data={state_info} value="readings" title="Total Readings" fmt="num0" />
<BigValue data={state_info} value="good_days" title="Good Days" fmt="num0" />

## County Hotspots

<DataTable data={state_hotspots}>
  <Column id="county_name" title="County" />
  <Column id="unhealthy_days" title="Unhealthy Days" fmt="num0" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
  <Column id="max_aqi" title="Peak AQI" />
</DataTable>
