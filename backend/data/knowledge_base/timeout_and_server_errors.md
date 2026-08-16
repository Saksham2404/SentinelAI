# Timeout and Server Error Investigation

## Timeout Errors

Timeout errors occur when a service does not respond within the expected
time limit.

Common causes include:

- Slow downstream services
- Database performance problems
- Network latency
- Resource exhaustion
- Deadlocks
- High request volume

## HTTP 5xx Server Errors

Server errors indicate that the server was unable to successfully process
a request.

Common causes include:

- Application crashes
- Database failures
- Dependency failures
- Resource exhaustion
- Internal service errors

## Investigation Strategy

When timeout events and 5xx errors increase together:

1. Identify the affected service.
2. Check whether response time increased.
3. Check ERROR and CRITICAL log messages.
4. Identify downstream dependencies.
5. Compare the abnormal time window with normal windows.
6. Investigate infrastructure or resource issues.