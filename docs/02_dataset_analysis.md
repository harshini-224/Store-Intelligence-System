# Dataset Analysis

## Objective

Understand the available CCTV footage and determine how each camera contributes to visitor analytics.

---

# Camera Inventory

## Camera 1 — Main Entrance

Purpose:
Visitor ingress and egress monitoring.

Potential Business Events:

* ENTRY
* EXIT
* REENTRY

Questions to Validate:

* Is the entry threshold clearly visible?
* Can direction be determined reliably?
* Are multiple people entering simultaneously?

Observations:
(To be filled after inspection)

---

## Camera 2 — Billing Counter

Purpose:
Queue and purchase behavior analysis.

Potential Business Events:

* BILLING_QUEUE_JOIN
* BILLING_QUEUE_ABANDON

Questions to Validate:

* Is queue formation visible?
* Is billing counter visible?
* Can waiting customers be distinguished?

Observations:
(To be filled after inspection)

---

## Camera 3 — Store Floor A

Purpose:
Customer browsing behavior.

Potential Business Events:

* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL

Questions to Validate:

* Which zones are visible?
* How much occlusion exists?

Observations:
(To be filled after inspection)

---

## Camera 4 — Store Floor B

Purpose:
Additional customer movement analysis.

Potential Business Events:

* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL

Observations:
(To be filled after inspection)

---

## Camera 5 — Low Traffic Area

Purpose:
Dead-zone monitoring and heatmap generation.

Potential Business Events:

* ZONE_ENTER
* ZONE_DWELL

Observations:
(To be filled after inspection)

---

# Global Dataset Challenges

Potential Challenges:

* Partial occlusions
* Group movement
* Crowded billing area
* Visitor overlap
* Camera angle distortion
* Low traffic regions

Observations:
(To be filled after inspection)

---

# Initial Engineering Assumptions

1. Each camera is fixed and stationary.
2. Videos represent the same store environment.
3. Human detection is feasible using pretrained models.
4. Camera timestamps may need synchronization.
5. Entry camera serves as source of truth for visitor counts.

---

# Expected Analytics Capability

| Camera      | Main Contribution   |
| ----------- | ------------------- |
| Entrance    | Visitor Count       |
| Billing     | Queue Analytics     |
| Floor A     | Dwell Analytics     |
| Floor B     | Zone Analytics      |
| Corner Area | Dead Zone Detection |

---

# Dataset Feasibility Assessment

## Strongly Supported Features

- Visitor Detection
- Visitor Tracking
- Entry Detection
- Exit Detection
- Zone Analytics
- Dwell Time Analytics
- Heatmap Generation

## Partially Supported Features

- Queue Analytics

## Unsupported / Low Confidence Features

- Staff Identification
- Reliable Cross-Camera Re-Identification

## Recommended MVP Scope

Video
→ Detection
→ Tracking
→ Entry/Exit Events
→ Zone Events
→ Analytics API
→ Dashboard

