# Store Intelligence System

## Overview

Store Intelligence System is an end-to-end retail analytics platform that transforms raw CCTV footage into actionable business insights.

The system processes video streams from multiple store cameras, detects and tracks visitors, generates behavioral events, computes retail analytics, and exposes insights through APIs and dashboards.

The objective is to provide physical retail stores with analytics capabilities similar to those available in modern e-commerce platforms.

---

# Problem Statement

Retail stores generally have access to:

* Sales data
* Billing records
* Inventory information

However, they lack visibility into customer behavior.

Store managers cannot easily answer:

* How many visitors entered the store?
* How many visitors completed a purchase?
* Which store sections attract the most attention?
* Where do customers drop off before purchasing?
* Are queues affecting conversion rates?
* Are there operational anomalies occurring in real time?

This project addresses these challenges by converting CCTV footage into structured business intelligence.

---

# Business Objectives

## Primary Objective

Measure and improve offline store conversion rate.

### Conversion Rate

Purchasing Visitors / Total Visitors

---

## Secondary Objectives

* Visitor counting
* Entry and exit tracking
* Zone analytics
* Queue monitoring
* Dwell time analysis
* Funnel analysis
* Anomaly detection

---

# Input Data

The current dataset consists of five CCTV video feeds captured from different areas of a retail store.

## Available Camera Views

### Camera 1: Main Entrance

Purpose:

* Visitor entry detection
* Visitor exit detection
* Traffic analysis

Expected Events:

* ENTRY
* EXIT
* REENTRY

---

### Camera 2: Billing Counter

Purpose:

* Queue monitoring
* Billing activity observation

Expected Events:

* BILLING_QUEUE_JOIN
* BILLING_QUEUE_ABANDON

---

### Camera 3: Store Floor View A

Purpose:

* Customer movement tracking
* Zone activity analysis

Expected Events:

* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL

---

### Camera 4: Store Floor View B

Purpose:

* Additional zone coverage
* Cross-camera tracking support

Expected Events:

* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL

---

### Camera 5: Low-Traffic Store Area

Purpose:

* Dead-zone detection
* Heatmap generation

Expected Events:

* ZONE_ENTER
* ZONE_DWELL

---

# Expected System Output

The system produces structured visitor events.

Example:

```json
{
  "visitor_id": "VIS_001",
  "event_type": "ENTRY",
  "timestamp": "2026-05-30T10:05:00Z",
  "camera_id": "CAM_ENTRY"
}
```

These events are later transformed into business metrics.

---

# Functional Requirements

## Visitor Detection

The system shall detect all visible customers from CCTV footage.

---

## Visitor Tracking

The system shall maintain consistent identities across video frames.

---

## Re-Identification

The system shall recognize visitors who temporarily leave and reappear.

---

## Event Generation

The system shall generate business events including:

* ENTRY
* EXIT
* REENTRY
* ZONE_ENTER
* ZONE_EXIT
* ZONE_DWELL
* BILLING_QUEUE_JOIN
* BILLING_QUEUE_ABANDON

---

## Analytics

The system shall compute:

* Visitor Count
* Conversion Rate
* Average Dwell Time
* Queue Metrics
* Heatmaps
* Funnel Metrics

---

## API Services

The system shall expose analytics through REST endpoints.

Examples:

* /health
* /metrics
* /funnel
* /heatmap
* /anomalies

---

# System Architecture

Raw CCTV Footage
↓
Person Detection
↓
Multi-Object Tracking
↓
Visitor Re-Identification
↓
Event Generation
↓
Event Storage
↓
Metrics Engine
↓
REST API
↓
Dashboard

---

# Technology Stack

## Computer Vision

* OpenCV
* YOLO

Purpose:
Human detection and frame processing.

---

## Tracking

* ByteTrack

Purpose:
Maintain visitor identity across frames.

---

## Re-Identification

* TorchReID
* OSNet

Purpose:
Detect returning visitors.

---

## Backend

* FastAPI

Purpose:
Expose analytics APIs.

---

## Database

* SQLite

Purpose:
Store events and metrics.

---

## Dashboard

* Streamlit

Purpose:
Real-time visualization.

---

## Containerization

* Docker
* Docker Compose

Purpose:
Portable deployment.

---

# Repository Structure

store-intelligence-system/

├── docs/
├── data/
├── pipeline/
├── app/
├── dashboard/
├── tests/
├── outputs/
├── docker-compose.yml
├── requirements.txt
└── README.md

---

# Development Roadmap

## Phase 1

Dataset Analysis

Deliverables:

* Camera understanding
* Video metadata extraction
* Zone identification

---

## Phase 2

Detection Pipeline

Deliverables:

* Human detection
* Annotated videos

---

## Phase 3

Tracking Pipeline

Deliverables:

* Persistent track IDs
* Visitor trajectories

---

## Phase 4

Event Generation

Deliverables:

* Entry events
* Exit events
* Zone events

---

## Phase 5

Event Storage

Deliverables:

* Database schema
* Event persistence

---

## Phase 6

Analytics Engine

Deliverables:

* Visitor metrics
* Conversion metrics
* Funnel analytics

---

## Phase 7

API Layer

Deliverables:

* REST endpoints
* Queryable analytics

---

## Phase 8

Dashboard

Deliverables:

* Real-time metrics
* Operational monitoring

---

# Success Criteria

A successful system should answer:

1. How many visitors entered the store?
2. How many completed a purchase?
3. Which zones received the highest engagement?
4. Are queues affecting conversion?
5. Are there operational anomalies requiring attention?

The final outcome is a production-oriented retail intelligence platform built from raw CCTV footage.
