# Notification Service Troubleshooting Guide

## Common Issues

### Delayed Delivery
- **Symptoms**: "Delayed delivery: backend service unavailable", notification queue growing
- **Root Causes**:
  - Upstream service dependency failure (auth, payment)
  - Message queue backpressure
  - Rate limiting by push notification provider (FCM, APNs)
  - Worker thread pool exhaustion
- **Investigation Steps**:
  1. Check dependency service health (auth, payment, database)
  2. Monitor message queue depth and consumer lag
  3. Review push provider rate limit responses
  4. Check worker thread pool utilization

### Service Unreachable
- **Symptoms**: "Authentication service unreachable", cascading notification failures
- **Root Causes**:
  - Network partition between notification and auth services
  - Auth service outage propagating downstream
  - DNS resolution failure
  - Service mesh sidecar crash
- **Investigation Steps**:
  1. Verify network connectivity between services
  2. Check upstream service health endpoints
  3. Review DNS resolution and TTL settings
  4. Check service mesh proxy status
