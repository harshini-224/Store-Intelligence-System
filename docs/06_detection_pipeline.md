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
