# Kubernetes Pod Failures and Troubleshooting

This document outlines common root causes and troubleshooting steps for Kubernetes pod failures, specifically focused on container runtime issues, scheduling failures, and memory limits.

## 1. CrashLoopBackOff

### Symptom
A pod starts, crashes, and restarts repeatedly. The status changes to `CrashLoopBackOff`.

### Common Causes
- **Application configuration errors:** Missing environment variables, incorrect config paths, or database credentials.
- **Dependency unavailability:** The application attempts to connect to a database or external service that is down and fails immediately.
- **Port collision:** The application tries to bind to a port that is already in use by another container in the same network namespace.
- **Permissions issues:** The container runs as a non-root user and tries to write to a directory restricted to root.

### Resolution Steps
1. Inspect pod logs:
   ```bash
   kubectl logs <pod-name> --previous
   ```
2. Check env variables and volume mounts.
3. Verify external dependencies are reachable.

---

## 2. OOMKilled (Out of Memory)

### Symptom
Container crashes with Exit Code 137. Pod description shows `OOMKilled`.

### Common Causes
- **Insufficient memory limits:** The memory limit set in the deployment spec is lower than the application's runtime requirement.
- **Memory leaks:** The application consumes memory continuously and does not release it, hitting the cgroup threshold.
- **Large batch jobs:** Processing a large payload that exceeds the container's heap space.

### Resolution Steps
1. Check event log:
   ```bash
   kubectl describe pod <pod-name>
   ```
2. Increase the resource limits in the deployment YAML:
   ```yaml
   resources:
     limits:
       memory: "2Gi"
     requests:
       memory: "1Gi"
   ```
