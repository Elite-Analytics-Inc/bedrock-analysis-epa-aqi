---
title: States
sidebar_position: 2
---

```sql all_states
SELECT REPLACE(state_name, '"', '') AS state_name,
       readings::BIGINT AS readings,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi,
       good_days::BIGINT AS good_days,
       not_good_days::BIGINT AS not_good_days
FROM results.states
ORDER BY avg_aqi DESC
```

# State Air Quality Comparison

<DataTable data={all_states} search=true rows=20>
  <Column id="state_name" title="State" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
  <Column id="max_aqi" title="Peak AQI" />
  <Column id="good_days" title="Good Days" fmt="num0" />
  <Column id="not_good_days" title="Not Good" fmt="num0" />
  <Column id="readings" title="Readings" fmt="num0" />
</DataTable>

<BarChart
  data={all_states}
  x="state_name"
  y="avg_aqi"
  swapXY=true
  title="All States by Average AQI"
  colorPalette={["#F59E0B"]}
  chartAreaHeight=1400
/>
