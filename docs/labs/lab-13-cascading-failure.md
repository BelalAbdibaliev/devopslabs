# Lab 13 - Cascading Failure

## Objective
Observe how a slow dependency crashes the system.

## Initial State
Normal state.

## Steps
1. Trigger Cascading Failure incident.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** Who fails first?
**Expected Observation:** Gateway times out waiting for OrderService.

## Troubleshooting Hints
- Check thread pool starvation.
