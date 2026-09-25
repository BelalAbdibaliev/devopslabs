# Lab 11 - Log Investigation

## Objective
Find errors using structured logs.

## Initial State
Trigger Error Storm incident.

## Steps
1. Use Grafana Loki, query {app="productservice"} |= "error".
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** Is there a TraceID attached?
**Expected Observation:** Yes.

## Troubleshooting Hints
- Ensure OTel is configured in logs.
