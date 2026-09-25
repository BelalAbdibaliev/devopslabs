# Lab 14 - Incident Investigation

## Objective
Find the root cause of a combined outage.

## Initial State
Trigger Combined Outage (Incident 10).

## Steps
1. Look at Grafana Overview. Identify the broken pieces. Trace errors to their source.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** What is the root cause?
**Expected Observation:** Redis Outage + DB Error.

## Troubleshooting Hints
- Use Traces to find the first failing span.
