# Lab 10 - Distributed Tracing

## Objective
Trace a request end-to-end.

## Initial State
Generate normal traffic.

## Steps
1. Open Grafana Tempo, find a trace from Gateway to DependencyService.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** Can you see the DB query time?
**Expected Observation:** Yes, Npgsql spans are visible.

## Troubleshooting Hints
- Copy TraceID from Loki.
