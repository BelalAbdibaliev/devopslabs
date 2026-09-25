# Lab 4 - Memory Pressure / OOMKilled

## Objective
Trigger an OOMKilled event.

## Initial State
Normal load.

## Steps
1. Use Control UI to allocate 256MB in MemoryWorker (which has a 128MB limit).
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** What happens to the pod?
**Expected Observation:** It gets OOMKilled and restarts.

## Troubleshooting Hints
- Check kubectl describe pod.
