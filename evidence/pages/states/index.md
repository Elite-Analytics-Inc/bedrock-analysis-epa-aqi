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
ORDER BY state_name
```

```sql selected_state_hotspots
SELECT REPLACE(state_name, '"', '') AS state_name,
       REPLACE(county_name, '"', '') AS county_name,
       unhealthy_days::INT AS unhealthy_days,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi
FROM results.hotspots
WHERE REPLACE(state_name, '"', '') = COALESCE(NULLIF('${inputs.selected_state.value}',''), 'California')
ORDER BY unhealthy_days DESC
```

```sql selected_state_info
SELECT REPLACE(state_name, '"', '') AS state_name,
       readings::BIGINT AS readings,
       avg_aqi::DOUBLE AS avg_aqi,
       max_aqi::INT AS max_aqi,
       good_days::BIGINT AS good_days,
       not_good_days::BIGINT AS not_good_days
FROM results.states
WHERE REPLACE(state_name, '"', '') = COALESCE(NULLIF('${inputs.selected_state.value}',''), 'California')
```

# State Detail

<Dropdown name="selected_state" data={all_states} value="state_name" title="Select State" defaultValue="California" />

<BigValue data={selected_state_info} value="avg_aqi" title="Average AQI" fmt="num1" />
<BigValue data={selected_state_info} value="max_aqi" title="Peak AQI" />
<BigValue data={selected_state_info} value="readings" title="Readings" fmt="num0" />
<BigValue data={selected_state_info} value="good_days" title="Good Days" fmt="num0" />

## County Hotspots in {inputs.selected_state.value}

<DataTable data={selected_state_hotspots}>
  <Column id="county_name" title="County" />
  <Column id="unhealthy_days" title="Unhealthy Days" fmt="num0" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
  <Column id="max_aqi" title="Peak AQI" />
</DataTable>

## All States Overview

<BarChart
  data={all_states}
  x="state_name"
  y="avg_aqi"
  swapXY=true
  title="All States by Average AQI"
  colorPalette={["#F59E0B"]}
  chartAreaHeight=1400
/>
