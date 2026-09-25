# Lab 9 - RabbitMQ Backlog

## Objective
Investigate message queue bottlenecks.

## Initial State
Normal processing.

## Steps
1. Stall consumers via Control API. Generate 5000 msg/sec load.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** How fast does queue grow?
**Expected Observation:** Very fast.

## Troubleshooting Hints
- Check Grafana RabbitMQ dashboard.
