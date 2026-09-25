# Lab 1 - Docker Networking

## Objective
Understand how containers communicate inside Docker Compose.

## Initial State
Start all containers.

## Steps
1. Use docker network inspect and ping between containers.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** How does Gateway find OrderService?
**Expected Observation:** DNS resolution via Docker DNS.

## Troubleshooting Hints
- Check docker-compose.yml networks.
