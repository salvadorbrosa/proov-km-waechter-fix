# What I checked, and what the agent got wrong

## What the agent got wrong

The original code had three distinct bugs, not one.

First, `wear_percent` used integer floor division (`//`) instead of true division (`/`), so any car with fewer kilometres than one full interval always reported 0% wear — the nearly-worn VOS-4471 at 14,900 km showed 0% instead of ~99%.

Second, `needs_service` fell back to `last_service_km = 0` when the key was missing, which made the car look as if it had never been serviced and had driven every kilometre since — so VOS-7788 at 92,000 km was wrongly flagged for service.

Third, the km-to-miles constant was inverted. The file stored `1.609`, which is kilometres *per* mile, not miles per kilometre. Multiplying by that number made 100 km come out as ~161 "miles" instead of ~62.

There was also a `//` floor division in `fleet_summary` that silently discarded the decimal part of the average wear, and a bare `car["last_service_km"]` in `car_wear` that crashed the whole nightly report if any car lacked that field.

## What I checked before I accepted its work

I ran `python verify.py` before and after every edit. Before fixing: 2 of 11 checks passed. After the fixes: I confirmed `wear_percent(14900, 15000)` returns ~99.3, that `needs_service({"id": "VOS-7788", "odometer": 92000})` returns `False`, that `km_to_miles(100)` returns ~62.1, and that the average-wear test passes with the expected ~59.67. I also ran `python -m pytest test_km_wachter.py test_fleet_report.py` to make sure both existing tests and the new one pass. `SERVICE_INTERVAL_KM` and `WARN_AT_PERCENT` in km_wachter.py and the values in settings.cfg were left untouched at 15000 and 80.

## What the data actually said

I compared the mean of every column for cars that broke down versus cars that did not. The obvious candidates — total odometer and age in years — turned out to have almost no difference in group means: a car that broke down was no older and had no more total mileage than one that stayed healthy. The columns that actually separated the two groups were `avg_daily_km` (cars driven harder each day broke down more) and `load_factor` (higher load, higher risk). `km_since_service` added a smaller signal. The risk score weights those three columns at 50%, 35%, and 15% respectively.
