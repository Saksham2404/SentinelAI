# Nginx Access Errors and Upstream Timeouts

This document focuses on diagnosing 5xx status codes in Nginx access logs and handling gateway timeouts.

## 1. 502 Bad Gateway

### Symptom
Nginx access logs show `502 Bad Gateway`. Client requests fail with a 502 error code.

### Common Causes
- **Downstream application offline:** The upstream server (FastAPI, Node.js, Gunicorn) has crashed or is not running.
- **Incorrect port mapping:** Nginx is configured to forward requests to the wrong port or socket path.
- **Firewall blocking:** Direct system firewall is preventing Nginx from accessing the localhost backend.

### Resolution Steps
1. Inspect Nginx error logs:
   ```bash
   tail -n 100 /var/log/nginx/error.log
   ```
2. Verify backend status:
   ```bash
   systemctl status backend-service
   ```
3. Test connection from Nginx host to backend port using netcat or curl.

---

## 2. 504 Gateway Timeout

### Symptom
Access logs record a `504` status code. Client receives timeout after 60 seconds.

### Common Causes
- **Slow database queries:** The backend service is waiting indefinitely for SQL responses.
- **Resource starvation:** CPU or RAM limits are hit, causing high response times on backend tasks.
- **Missing timeout configurations:** Nginx's `proxy_read_timeout` is shorter than the time needed for the application to process the request.

### Resolution Steps
1. Increase timeout values in Nginx configuration:
   ```nginx
   proxy_read_timeout 300s;
   proxy_connect_timeout 300s;
   ```
2. Check backend system performance metrics.
