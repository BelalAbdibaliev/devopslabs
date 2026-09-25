# Lab 6 - Kubernetes Probes

## Objective
Understand liveness and readiness probes.

## Initial State
System deployed in K8s.

## Steps
1. Inject a deadlock or error storm, see liveness probe fail.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** How long until restart?
**Expected Observation:** About 15 seconds.

## Troubleshooting Hints
- Check kubectl describe pod for probe failures.
