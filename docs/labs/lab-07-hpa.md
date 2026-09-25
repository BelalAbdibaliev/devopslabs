# Lab 7 - HPA

## Objective
Observe Horizontal Pod Autoscaling.

## Initial State
Order Service at 2 replicas.

## Steps
1. Run k6 load.js. Watch CPU rise and HPA scale replicas.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** What is the max replicas?
**Expected Observation:** 10.

## Troubleshooting Hints
- Check kubectl get hpa -w.
