# Tracking Pipeline

## Objective

Assign persistent identities to detected visitors.

---

## Algorithm

ByteTrack

---

## Input

Person detections from YOLO.

---

## Output

Tracked visitors.

Example:

{
    "track_id": 7,
    "bbox": [100,200,300,500]
}

---

## Business Impact

Tracking enables:

- Visitor counting
- Entry detection
- Exit detection
- Dwell time computation
- Zone analytics