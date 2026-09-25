# Lab 8 - KEDA

## Objective
Observe event-driven autoscaling.

## Initial State
Notification Service at 1 replica.

## Steps
1. Generate RabbitMQ backlog via Control API. Watch KEDA add pods.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** Does it scale before CPU rises?
**Expected Observation:** Yes, based on queue length.

## Troubleshooting Hints
- Check kubectl get scaledobjects.
