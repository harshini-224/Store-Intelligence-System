# 13. Heuristic Group Detection

## Philosophy
Individual visitors in a retail store often move in natural groups (families, friends). For accurate conversion metrics, we count individuals, but for marketing and loyalty analysis, understanding group behavior is critical.

## Detection Logic
- **Module**: `data/pipeline/tracking/group_detector.py`
- **Algorithm**: Heuristic-based co-movement analysis.

### Criteria for Grouping
1.  **Spatial Proximity**: Two visitors must be within a `DISTANCE_THRESHOLD` (default 150px).
2.  **Temporal Consistency**: The proximity must be maintained for at least `FRAME_THRESHOLD` (default 15 frames).
3.  **Velocity Similarity**: Visitors must be moving in roughly the same direction at similar speeds (`VELOCITY_THRESHOLD`).

## Metadata Propagation
Once a group is detected, a unique `group_id` is assigned and stored in the `metadata` field of all canonical events generated for those individuals.

```json
"metadata": {
  "group_id": "GROUP_ABC_123",
  "is_staff": false
}
```

## Benefits and Limits
- **Benefits**: Lightweight, no external models required, runs in real-time.
- **Limits**: Can be challenging in very high-density corridors; works best in browsing zones.
