import json


def load_floor_metrics():

    result = {}

    files = [
        "data/outputs/analytics/floor_a_summary.json",
        "data/outputs/analytics/floor_b_summary.json"
    ]

    for file in files:

        try:

            with open(file) as f:

                result[file] = json.load(f)

        except:

            result[file] = {}

    return result