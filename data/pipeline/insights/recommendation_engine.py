class RecommendationEngine:

    def generate(self, analytics):

        recommendations = []

        for zone, data in analytics.items():
            if zone.startswith("_"):
                continue
            if not isinstance(data, dict):
                continue
            if "visitors" not in data or "total_dwell_time" not in data:
                continue

            if data["visitors"] < 10:

                recommendations.append(
                    f"Low engagement in {zone}. Consider promotions."
                )

            if data["total_dwell_time"] > 300:

                recommendations.append(
                    f"{zone} has high dwell time. Upsell opportunities exist."
                )

        return recommendations
