# PVE Node Exporter Discovery

This microservice is intended to allow for auto-discovery of Prometheus Node Exporters running
on Proxmox VE guests. It can be run as a standalone python script, or using the docker container
hosted at 14agerber/pve_node_exporter_discovery:latest.

As sample config for Prometheus is provided below:
```
-job_name: pve_node_exporter
  scheme: http
  metrics_path: /metrics
  params:
    prometheus:
    - http<s>://<prometheus URL>
  http_config:
  - url: http://<discovery_server>:24684
```
