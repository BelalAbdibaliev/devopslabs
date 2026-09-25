# Lab 3 - CPU Throttling

## Objective
Generate CPU load and observe throttling.

## Initial State
Normal load.

## Steps
1. Use Control UI to start CPU Stress (90%) on CpuWorker. Observe Grafana process_cpu_time_seconds_total.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** Does the container exceed limits?
**Expected Observation:** No, Kubernetes/Docker throttles it.

## Troubleshooting Hints
- Check Grafana CPU dashboard.
