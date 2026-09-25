# Lab 15 - Recovery

## Objective
Restore service after an incident.

## Initial State
System is broken (Incident 10 active).

## Steps
1. Click 'Emergency Stop' or 'Reset' in Control UI. Watch metrics recover.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** How fast does error rate drop?
**Expected Observation:** Instantly.

## Troubleshooting Hints
- Check if queue backlogs take time to process.
