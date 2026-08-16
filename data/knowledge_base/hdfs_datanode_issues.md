# HDFS DataNode Issues

## DataNode Connection Failure

A DataNode may become unavailable because of network connectivity problems,
disk failures, process crashes, or insufficient system resources.

Common symptoms include:

- Connection refused errors
- DataNode heartbeat missing
- Block replication warnings
- Slow read or write operations
- DataNode process termination

## Investigation Steps

1. Check whether the DataNode process is running.
2. Check network connectivity between NameNode and DataNode.
3. Check available disk space.
4. Review DataNode logs for ERROR or WARN messages.
5. Check for repeated connection failures.
6. Check whether block replication is increasing.

## Possible Root Causes

- Network failure
- Disk full
- DataNode process crash
- High CPU or memory usage
- Incorrect configuration