def calculate_roi(reward_amount, time_est_min, currency="USD"):
    """Calcul du ROI en $/min."""
    currency_rates = {"XP": 0.01, "GAL": 0.50, "POINTS": 0.005}
    usd_value = reward_amount * currency_rates.get(currency, 1.0)
    return usd_value / max(time_est_min, 1)
