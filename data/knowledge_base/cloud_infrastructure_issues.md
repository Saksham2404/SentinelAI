# Cloud Infrastructure and Disk I/O Bottlenecks

This guide covers cloud infrastructure issues, specifically focusing on disk IOPS saturation, network throttling, and local SSD failures.

## 1. Disk IOPS Throttling

### Symptom
High latency on data reads/writes. Storage IOPS metrics hit maximum limits. Log generation becomes delayed.

### Common Causes
- **Incorrect disk tiering:** Running high-volume log or database storage on slow, standard mechanical or general-purpose SSD storage tiers.
- **Burstable quota exhaust:** Burstable credits are depleted, capping disk throughput to baseline.

### Resolution Steps
1. Monitor disk latency metrics.
2. Upgrade storage class (e.g., from gp2 to gp3 with dedicated IOPS in AWS, or premium disk in Azure).
3. Distribute files across multiple logical volumes.

---

## 2. Ephemeral Storage Failures

### Symptom
Read-only file system errors in logs. Failure to mount scratch directories or write diagnostic output.

### Common Causes
- **Host hypervisor degradation:** Physical disk backing local instance storage crashed.
- **Volume space exhaustion:** Application fills disk space without log rotation, corrupting filesystem descriptors.

### Resolution Steps
1. Verify disk space utilization:
   ```bash
   df -h
   ```
2. Setup automated log rotation:
   ```bash
   logrotate -f /etc/logrotate.conf
   ```
