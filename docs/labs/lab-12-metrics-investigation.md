# Lab 12 - Metrics Investigation

## Objective
Query PromQL for custom metrics.

## Initial State
System under load.

## Steps
1. Query devops_lab_requests_total.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** What is the RPS?
**Expected Observation:** Varies by load script.

## Troubleshooting Hints
- Use rate() function in PromQL.
