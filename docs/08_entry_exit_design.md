# Entry and Exit Boundary Design

## Objective

The objective of this module is to detect customer entry and exit events using CCTV footage from the entrance camera. A virtual boundary is created at the store entrance, and tracked visitors are monitored to determine whether they are entering or leaving the store.

---

## Problem Statement

The entrance camera is positioned at an angle and does not provide a straight overhead view of the store entrance.

Because of this camera perspective:

- The physical entrance does not appear as a horizontal line.
- A simple horizontal boundary can generate false entry and exit events.
- People moving inside the store may cross a horizontal line without actually leaving the store.
- People walking in the mall corridor may be incorrectly counted as store visitors.

Therefore, a more accurate entrance boundary is required.

---

## Observation and Analysis

The entrance camera footage was analyzed frame by frame to understand the physical layout of the store.

During analysis, an individual was observed standing near the entrance region. This helped identify the approximate transition area between:

- Store Interior
- Entrance Area
- Mall Corridor

The position of the observed individual was used only as a visual reference to estimate the entrance region.

The individual was **not used in the entry/exit detection logic** and was **not treated as a special tracking target**.

---

## Store Layout Understanding

The entrance camera shows three distinct regions:

### Store Interior

This area contains:

- Product displays
- Customer browsing area
- Wooden flooring

### Entrance Zone

This area contains:

- Entrance mat
- Glass door region
- Immediate entry pathway

### Mall Corridor

This area contains:

- Public walking pathway
- Non-store visitors
- Passersby

A customer entering the store must move from the corridor side toward the store interior.

A customer exiting the store must move from the store interior toward the corridor side.

---

## Why a Horizontal Line Was Rejected

Initially, a horizontal entrance boundary was considered.

Example:

```text
-------------------------
      ENTRY LINE
-------------------------
```

However, due to the camera angle, the actual entrance path is diagonal.

Problems observed with a horizontal boundary:

- False entry detections.
- False exit detections.
- Store customers crossing the line while browsing.
- Corridor pedestrians being counted incorrectly.

Therefore, a horizontal boundary was not suitable for this camera view.

---

## Selected Solution

A diagonal virtual boundary was chosen because it better represents the physical entrance structure visible in the CCTV footage.

The diagonal line follows the natural separation between:

- Store interior
- Mall corridor

This significantly reduces false event generation.

---

## OpenCV Coordinate System

The entrance boundary is defined using OpenCV image coordinates.

Coordinate System:

```text
(0,0)
   +----------------------> X
   |
   |
   |
   |
   v
   Y
```

For a Full HD frame:

```text
Top Left     = (0,0)

Top Right    = (1920,0)

Bottom Left  = (0,1080)

Bottom Right = (1920,1080)
```

---

## Entrance Boundary Configuration

The virtual entrance line is defined using two points.

```python
ENTRY_LINE_START = (850, 1080)
ENTRY_LINE_END   = (1550, 0)
```

Where:

### ENTRY_LINE_START

Represents the point where the boundary touches the bottom edge of the frame.

```text
Bottom Edge
     ▲
     |
(850,1080)
```

### ENTRY_LINE_END

Represents the point where the boundary touches the top edge of the frame.

```text
Top Edge
     ▲
     |
(1550,0)
```

The line is drawn using:

```python
cv2.line(
    frame,
    ENTRY_LINE_START,
    ENTRY_LINE_END,
    (0, 0, 255),
    3
)
```

---

## Visual Interpretation

The red diagonal line divides the frame into two logical regions.

```text
Store Interior
      |
      |
      |
      |\
      | \
      |  \
      |   \
      |    \
      |     \
      |      \
      +-------\ Mall Corridor
```

### Left Side of Line

Represents:

- Store Interior
- Customer Area

### Right Side of Line

Represents:

- Mall Corridor
- Outside Area

---

## Entry Detection Logic

A visitor is considered to have entered the store when:

```text
Mall Corridor
      ↓
Crosses Boundary
      ↓
Store Interior
```

The event generated:

```json
{
  "event_type": "ENTRY"
}
```

---

## Exit Detection Logic

A visitor is considered to have exited the store when:

```text
Store Interior
      ↓
Crosses Boundary
      ↓
Mall Corridor
```

The event generated:

```json
{
  "event_type": "EXIT"
}
```

---

## Boundary Validation

The boundary placement was validated by observing multiple video segments and ensuring:

### Correct Behavior

- Customers entering cross the boundary.
- Customers exiting cross the boundary.
- Entry path aligns with the physical store entrance.

### Incorrect Behavior Prevented

- People standing inside the store are not counted as exits.
- Mall pedestrians are not counted as entries.
- Customers browsing near the entrance are not counted repeatedly.

---

## Design Decision Summary

| Component | Decision |
|------------|------------|
| Camera Type | Angled CCTV View |
| Boundary Type | Diagonal Virtual Line |
| Calibration Method | Manual Visual Calibration |
| Validation Method | CCTV Observation |
| Purpose | Entry/Exit Event Detection |
| Benefit | Reduced False Positives |

---

## Conclusion

A diagonal virtual entrance boundary was selected because it closely follows the actual store entrance visible in the CCTV footage.

The boundary was manually calibrated through visual inspection of the entrance area and validated against observed pedestrian movement.

This approach provides a practical and reliable solution for entry and exit event detection while minimizing false event generation caused by camera perspective and customer movement inside the store.