# 16. Insights & Business Recommendations

## Overview
The system uses a rule-based engine to transform raw counts into actionable business recommendations. These are served via the `/recommendations` and `/ai-insights` endpoints.

## Recommendation Logic
The engine evaluates store performance across three dimensions:

### 1. Retention & Dwell
- **Trigger**: High dwell time in browsing zones but low conversion.
- **Insight**: "Engagement is high, but closure is low."
- **Recommendation**: "Deploy staff to the SkinCare/Makeup stations to assist with product selection."

### 2. Transaction Friction
- **Trigger**: High queue abandonment rate (>15%).
- **Insight**: "Queuing friction is costing potential sales."
- **Recommendation**: "Incentivize self-checkout or optimize counter staffing during peak hours."

### 3. Traffic Flow
- **Trigger**: Dead zones identified in heatmap (0 engagement).
- **Insight**: "Store layout is not attracting visitors to specific aisles."
- **Recommendation**: "Move high-margin promo items to the main walkway hotspot."

## Multi-Store Aggregation
The `insights_service` aggregates these signals across multiple floors to provide a prioritized action list for a City Manager or Store Manager.
