# Lab 2 - Container Resource Limits

## Objective
Observe what happens when limits are breached.

## Initial State
System running normally.

## Steps
1. Check cgroups and inspect container limits.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** What is the CPU limit of CpuWorker?
**Expected Observation:** It matches docker-compose limits.

## Troubleshooting Hints
- Use docker stats.
