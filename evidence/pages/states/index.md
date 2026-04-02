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
       not_good_days::BIGINT AS not_good_days,
       '/states/' || REPLACE(state_name, '"', '') AS state_link
FROM results.states
ORDER BY state_name
```

# States

Click a state to see its county-level detail.

<DataTable data={all_states} search=true link="state_link">
  <Column id="state_name" title="State" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
  <Column id="max_aqi" title="Peak AQI" />
  <Column id="good_days" title="Good Days" fmt="num0" />
  <Column id="not_good_days" title="Not Good" fmt="num0" />
  <Column id="readings" title="Readings" fmt="num0" />
</DataTable>
