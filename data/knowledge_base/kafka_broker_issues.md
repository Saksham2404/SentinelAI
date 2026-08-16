# Apache Kafka Broker Failures and Consumer Lag

This document provides root causes and troubleshooting guidelines for Apache Kafka broker outages and critical consumer lag issues.

## 1. Under-Replicated Partitions (URPs)

### Symptom
Kafka cluster logs show high counts of Under-Replicated Partitions. Producers report timeout errors.

### Common Causes
- **Broker offline:** One or more brokers in the cluster crashed or became unresponsive.
- **Network partition:** Network latency between brokers exceeds the replica timeout (`replica.lag.time.max.ms`).
- **Disk I/O saturation:** A broker is overwhelmed by disk writes, falling behind on synchronization.

### Resolution Steps
1. Verify broker statuses:
   ```bash
   kafka-broker-api-versions.sh --bootstrap-server localhost:9092
   ```
2. Check replication status for affected topics:
   ```bash
   kafka-topics.sh --describe --topic <topic-name> --bootstrap-server localhost:9092
   ```
3. Restart unresponsive brokers and optimize disk metrics.

---

## 2. High Consumer Lag

### Symptom
Consumers are not processing messages fast enough. Lag metrics (`records-lag`) spike.

### Common Causes
- **Slow processing logic:** The consumer application is blocked on a database call or performing intensive computation per message.
- **Imbalanced partition assignment:** Consumers are not distributed evenly across topic partitions.
- **Frequent rebalances:** Slow consumers trigger heartbeat timeouts, causing continuous partition rebalancing.

### Resolution Steps
1. Monitor group lag:
   ```bash
   kafka-consumer-groups.sh --describe --group <group-name> --bootstrap-server localhost:9092
   ```
2. Increase consumer parallelism by adding more instances (up to the partition count).
3. Increase `max.poll.interval.ms` in consumer configs.
