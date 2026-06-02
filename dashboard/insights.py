import json


def generate_business_summary():

    with open(
        "data/outputs/analytics/floor_a_summary.json"
    ) as file:

        floor_a = json.load(file)

    top_zone = max(
        floor_a,
        key=lambda z:
        floor_a[z]["total_dwell_time"]
    )

    return (
        f"Highest customer engagement "
        f"observed in {top_zone}."
    )