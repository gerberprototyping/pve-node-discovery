# PVE Node Discovery

This microservice is intended to allow for auto-discovery of Prometheus Node Exporters running
on Proxmox VE guests. It can be run as a standalone python script, or using the docker container
hosted at `14agerber/pve-node-discovery:latest`.

PVE Exporter must already be set up so the service can query guest names.

<br>

### Sample config for Prometheus:
```
-job_name: pve-node-exporter
  params:
    prometheus: ['http<s>://<prometheus URL>']
  http_config:
    - url: http://<discovery_server>:9951/static-configs
```

<br>

Configuring node discovery can be done via command line arguments or environment variables.
The only required parameter is `prometheus-url`.
Lists are passed via command line using multiple arguments (ex: `--exclude foo --exclude bar`).
Environment variables use comma-separated lists (ex: `NODE_DISCOVERY_EXCLUDE='foo,bar'`).
The `map-from` and `map-to` parameters are used when the vm's/container's proxmox name is not the
same as its DNS name. They musted be provided in pairs (ex: `--map-from WebsiteVM --map-to www`).

| Argument | Env Variable | Default | Description |
| --- | --- | --- | --- |
| --listen-host | NODE_DISCOVERY_LISTEN_HOST | 0.0.0.0 | Server listen address |
| --listen-port | NODE_DISCOVERY_LISTEN_PORT | 9951 | Server listen port |
| --prometheus-url | NODE_DISCOVERY_PROMETHEUS_URL | **Required** | Prometheus base URL for making queries |
| --guest-domain | NODE_DISCOVERY_GUEST_DOMAIN | *none* | Domain to append to pve guest name |
| --guest-port | NODE_DISCOVERY_GUEST_PORT | 9100 | Port of node_exporter running on guests |
| --exclude | NODE_DISCOVERY_EXCLUDE | *none* | List of guests to exclude/skip |
| --map-from | NODE_DISCOVERY_MAP_FROM | *none* | Ordered list of guests requering mapping |
| --map-to | NODE_DISCOVERY_MAP_TO | *none* | Ordered list of dns names to map to |




<br>

> Requires Prometheus v2.29 or later