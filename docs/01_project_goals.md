# 01. Project Goals

## Overview
The Store Intelligence System is designed for the Purplle Engineering Hiring Challenge to bridge the data gap between online and offline retail. It transforms raw CCTV footage into high-fidelity behavioral analytics for physical stores.

## Key Objectives
1. **Visitor Analytics**: Accurately count unique visitors, track their movement, and calculate dwell times in specific store zones.
2. **Conversion Tracking**: Correlate in-store behavior with POS transaction data to understand the "Browse-to-Buy" funnel.
3. **Operational Efficiency**: Monitor queue depths and wait times to identify staffing bottlenecks.
4. **Actionable Insights**: Detect anomalies (e.g., sudden queue spikes) and provide automated recommendations for store managers.
5. **Production Readiness**: Provide a robust, containerized API with structured logging and standardized event exports (JSONL).

## Success Criteria
- Detection accuracy in crowded retail environments.
- Effective deduplication of visitors (re-entry handling).
- Clear distinction between customers and staff.
- High-performance processing of long-duration (20min+) video clips.
- Compliance with the canonical 9-field event schema.
