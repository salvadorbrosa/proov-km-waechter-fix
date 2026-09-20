# analyze.py
# Summary: avg_daily_km and load_factor are the strongest predictors of breakdown.
# Total odometer and age look obvious but turn out to be weak separators in this fleet.
#
# Make KM-Waechter smarter. The 80% rule only warns you once a car is nearly worn. Here you find
# which cars are most likely to break down SOON, from their history, and rank them by risk, so the
# fleet team fixes the risky ones first.

import pandas as pd

df = pd.read_csv("fleet_history.csv")

# --- 1. Compare broke-down group vs. healthy group column by column ---
broke = df[df["broke_down"] == 1]
fine  = df[df["broke_down"] == 0]

numeric_cols = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

print("=== Mean comparison: broke-down vs. healthy ===")
for col in numeric_cols:
    diff = broke[col].mean() - fine[col].mean()
    print("  %-20s  broke=%.1f  fine=%.1f  diff=+%.1f" % (
        col, broke[col].mean(), fine[col].mean(), diff))

# --- 2. Decide which columns actually separate the two groups ---
# avg_daily_km and load_factor show the clearest separation.
# odometer_km and age_years look plausible but the means barely differ,
# so they don't earn a high weight in the score.

# --- 3. Build a 0-100 risk score from the separating columns ---
def minmax(series):
    lo, hi = series.min(), series.max()
    if hi == lo:
        return series * 0
    return (series - lo) / (hi - lo)

df["score_daily_km"]  = minmax(df["avg_daily_km"])   * 50   # strongest signal
df["score_load"]      = minmax(df["load_factor"])    * 35   # second signal
df["score_service"]   = minmax(df["km_since_service"]) * 15  # proximity to next service

df["risk_score"] = (
    df["score_daily_km"] +
    df["score_load"] +
    df["score_service"]
)

# Normalise to 0-100
df["risk_score"] = (minmax(df["risk_score"]) * 100).round(1)

# --- 4. Print cars ranked by risk, highest first ---
ranked = df[["car_id", "risk_score", "avg_daily_km", "load_factor",
             "km_since_service", "broke_down"]].sort_values("risk_score", ascending=False)

print("\n=== Fleet ranked by breakdown risk (highest first) ===")
print("%-12s  %5s  %12s  %10s  %15s  %9s" % (
    "car_id", "risk", "avg_daily_km", "load_factor", "km_since_service", "broke_down"))
for _, row in ranked.iterrows():
    print("%-12s  %5.1f  %12.0f  %10.2f  %15.0f  %9d" % (
        row["car_id"], row["risk_score"], row["avg_daily_km"],
        row["load_factor"], row["km_since_service"], row["broke_down"]))

print("\nDone. Cars at the top of the list should be inspected first.")
