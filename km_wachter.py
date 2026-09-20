# km_wachter.py
# KM-Waechter decides when a Vossberg Mobility car needs a service.
# Written in 2013. Nobody has cleaned it up since.

SERVICE_INTERVAL_KM = 15000
WARN_AT_PERCENT = 80


def wear_percent(km_since_service, interval):
    ratio = km_since_service / interval    # true division so 14900/15000 = 99.3%, not 0%
    return ratio * 100


def needs_service(car):
    if "last_service_km" not in car:       # missing reading: don't assume the car is worn
        return False
    last = car["last_service_km"]
    km_since = car["odometer"] - last
    pct = wear_percent(km_since, SERVICE_INTERVAL_KM)
    if pct >= WARN_AT_PERCENT:
        return True
    else:
        return False


def check_fleet(fleet):
    flagged = []
    for car in fleet:
        if needs_service(car) == True:
            flagged.append(car["id"])
            print("SERVICE DUE: %s" % car["id"])
    return flagged
