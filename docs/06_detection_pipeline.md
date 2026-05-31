# Detection Pipeline

## Objective

Identify all customers visible in CCTV footage.

---

## Model

YOLO11n

---

## Input

Video Frame

---

## Output

List of Person Bounding Boxes

Example:

[
  {
    "bbox":[100,200,300,500],
    "confidence":0.93
  }
]

---

## Acceptance Criteria

- Detect visible customers
- Maintain real-time feasibility
- Minimize false positives

# Detection Validation

## Entrance Camera

Result:
PASS

Observations:
- Person detection successful
- Entry region clearly visible
- Low false positives

---

## Store Floor Camera

Result:
PASS

Observations:
- Multiple visitors detected
- Crowding handled reasonably well

---

## Billing Camera

Result:
NOT TESTED

Reason:
Will be validated during queue analytics implementation.