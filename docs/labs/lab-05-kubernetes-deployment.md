# Lab 5 - Kubernetes Deployment

## Objective
Deploy the stack to K8s.

## Initial State
Local K8s cluster ready.

## Steps
1. Run helm install devopslabs ./deploy/kubernetes/helm/devopslabs.
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** Are all pods running?
**Expected Observation:** Yes.

## Troubleshooting Hints
- Check kubectl get events.
