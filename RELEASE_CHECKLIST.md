# Release Checklist

Use this checklist before submitting the repository for review or demo.

## Documentation

- [ ] README complete.
- [ ] Architecture documentation complete.
- [ ] Design documentation complete.
- [ ] Pipeline flow documentation complete.
- [ ] Staff exclusion audit complete.
- [ ] Demo script complete.
- [ ] Validation checklist complete.

## Tests

- [ ] Staff exclusion tests passing.
- [ ] Health endpoint tests passing.
- [ ] Funnel analytics tests passing.
- [ ] Queue analytics tests passing.
- [ ] Smoke test passing or known failures documented.

Suggested commands:

```bash
python test_staff_exclusion.py
python test_health_endpoint.py
python data/pipeline/analytics/test_funnel_analytics.py
python run_smoke_test.py
```

On Windows, run queue tests with UTF-8 output:

```powershell
$env:PYTHONIOENCODING='utf-8'; python data\pipeline\analytics\test_queue_analytics.py
```

## Operational Checks

- [ ] Health endpoint verified.
- [ ] API verified.
- [ ] Dashboard verified.
- [ ] Sample outputs generated.
- [ ] Heatmaps generated.
- [ ] Analytics summaries generated.
- [ ] Tracking outputs generated.
- [ ] Event outputs generated and non-empty.

## API Checks

- [ ] `GET /health`
- [ ] `GET /metrics`
- [ ] `GET /metrics/conversion/summary`
- [ ] `GET /metrics/queue/summary`
- [ ] `GET /funnel`
- [ ] `GET /kpis`
- [ ] `GET /recommendations`
- [ ] `GET /anomalies`

## Dashboard Checks

- [ ] Streamlit dashboard starts.
- [ ] Upload form works.
- [ ] Pipeline button runs scripts.
- [ ] KPI row renders.
- [ ] Zone chart renders.
- [ ] Heatmap renders.
- [ ] Recommendations render.

## Demo Readiness

- [ ] A short demo video is available.
- [ ] Backup pre-generated outputs are available.
- [ ] API server command is known.
- [ ] Dashboard command is known.
- [ ] Demo script has been rehearsed in 3-5 minutes.
- [ ] Known limitations are ready to explain.
