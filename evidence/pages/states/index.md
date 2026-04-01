---
title: States
sidebar_position: 2
---

```sql all_states
SELECT state_name,
       readings,
       avg_aqi,
       max_aqi,
       good_days,
       not_good_days,
       '/states/' || state_name AS state_link
FROM states
ORDER BY state_name
```

# States

<DataTable data={all_states} search=true link="state_link">
  <Column id="state_name" title="State" />
  <Column id="avg_aqi" title="Avg AQI" fmt="num1" />
  <Column id="max_aqi" title="Peak AQI" />
  <Column id="good_days" title="Good Days" fmt="num0" />
  <Column id="not_good_days" title="Not Good" fmt="num0" />
  <Column id="readings" title="Readings" fmt="num0" />
</DataTable>
