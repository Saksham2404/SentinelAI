# Authentication Service Troubleshooting Guide

## Common Issues

### OutOfMemoryError / Heap Exhaustion
- **Symptoms**: "OutOfMemoryError: GC overhead limit exceeded", heap allocation limit reached, service crash
- **Root Causes**:
  - Memory leak in session management
  - Excessive session token caching without eviction
  - Large JWT payload accumulation
  - Insufficient JVM heap size for traffic volume
- **Investigation Steps**:
  1. Capture heap dump and analyze with MAT or JProfiler
  2. Check session store size and eviction policy
  3. Review JVM heap settings (-Xmx, -Xms)
  4. Monitor GC pause times and frequency

### Keystore Service Unresponsive
- **Symptoms**: "Keystore service became unresponsive!", token verification failures
- **Root Causes**:
  - HSM (Hardware Security Module) connection timeout
  - Certificate rotation in progress
  - Keystore file corruption or permission issues
  - Underlying crypto library deadlock
- **Investigation Steps**:
  1. Check HSM connectivity and health
  2. Verify certificate validity and rotation schedule
  3. Review keystore file permissions and integrity
  4. Check for thread deadlocks in crypto operations

### Authentication Rate Spikes / Brute Force
- **Symptoms**: "High rate of authentication requests: 1200/sec", rate limiting active, decryption failures
- **Root Causes**:
  - Credential stuffing or brute force attack
  - Misconfigured client retry logic causing amplification
  - Bot traffic surge
  - Session fixation or replay attacks
- **Investigation Steps**:
  1. Analyze authentication failure patterns by IP
  2. Check WAF/IDS alerts for attack signatures
  3. Review rate limiting thresholds and effectiveness
  4. Correlate with CDN/load balancer access logs

### Token Verification Failures
- **Symptoms**: "Authentication token check failed - 401", cascading auth failures across services
- **Root Causes**:
  - Token signing key rotation without propagation
  - Clock skew between auth server and validators
  - Expired or revoked tokens not cleared from cache
  - Auth service unavailable causing cascade
- **Investigation Steps**:
  1. Verify token signing keys match across services
  2. Check NTP synchronization on all nodes
  3. Review token cache TTL configuration
  4. Check auth service health and failover status
