# Database Service Troubleshooting Guide

## Common Issues

### Connection Pool Exhaustion
- **Symptoms**: Connection pool timeout errors, "Active: 50/50, Idle: 0", pending connection queue growing
- **Root Causes**:
  - Long-running queries holding connections
  - Connection leaks from unclosed transactions
  - Sudden traffic spike exceeding pool capacity
  - Slow queries blocking connection return
- **Investigation Steps**:
  1. Check active query count and execution times
  2. Review connection pool metrics (active, idle, pending)
  3. Look for uncommitted transactions
  4. Verify pool size configuration vs traffic volume

### Connection Refused / Reconnection Failures
- **Symptoms**: "Connection refused after 3 retries", failover to read-only backup
- **Root Causes**:
  - Database primary node crash or restart
  - Network partition between app and database
  - Max connections limit reached on database server
  - Firewall or security group changes blocking access
- **Investigation Steps**:
  1. Check database server health and uptime
  2. Verify network connectivity and DNS resolution
  3. Review database server max_connections setting
  4. Check recent infrastructure changes

### High Latency / Slow Queries
- **Symptoms**: Latency spikes >1000ms, connection acquisition delays
- **Root Causes**:
  - Missing or stale indexes
  - Table lock contention
  - Disk I/O bottleneck on database server
  - Query plan regression after statistics update
- **Investigation Steps**:
  1. Run EXPLAIN ANALYZE on slow queries
  2. Check table and row lock waits
  3. Monitor disk I/O utilization
  4. Review recent schema or index changes
