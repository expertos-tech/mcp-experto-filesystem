<!-- AGENTS SUMMARY
Operational guide for the local telemetry stack used to observe the MCP, its CLI,
and model usage signals when they are emitted.
Sessions:
- OVERVIEW: Purpose and scope of the stack.
- QUICKSTART: Startup and shutdown commands.
- PERSISTENCE: Local storage layout and cleanup guidance.
- INSTRUMENTATION: OTLP environment variables and telemetry conventions.
- TROUBLESHOOTING: Common local issues and checks.
-->

# Local Telemetry Operations

## Table of Contents

* [Overview](#overview)
* [Quickstart](#quickstart)
* [Persistence](#persistence)
* [Instrumentation](#instrumentation)
* [Troubleshooting](#troubleshooting)

---

<!-- START OVERVIEW -->
## Overview

This stack provides local, persistent, real-time observability for:

* `mcp-experto-filesystem`
* the CLI, agent, or host process that runs or consumes the MCP
* model usage signals, when the emitting process publishes them through OpenTelemetry

The stack is fully local and does not require authentication. It uses:

* OpenTelemetry Collector as the single OTLP entrypoint
* Prometheus for metrics
* Loki for logs
* Tempo for traces
* Grafana as the main exploration UI

Published local endpoints:

* `127.0.0.1:4317` for OTLP gRPC
* `127.0.0.1:4318` for OTLP HTTP
* `127.0.0.1:3000` for Grafana
* `127.0.0.1:9090` for Prometheus

The dashboard is designed to be useful immediately for collector health and OTLP traffic.
More specific views for model requests, tokens, cost, tool names, or session IDs depend
on the attributes actually emitted by the local application or CLI.
<!-- END OVERVIEW -->

---

<!-- START QUICKSTART -->
## Quickstart

Start the stack:

```bash
cd local-telemetry
docker compose up -d
```

Open Grafana:

```bash
open http://127.0.0.1:3000
```

On Linux, if `open` is not available:

```bash
xdg-open http://127.0.0.1:3000
```

Stop the stack:

```bash
docker compose down
```

Stop the stack and keep all collected data:

```bash
docker compose down
```

Stop the stack and remove only the containers and network:

```bash
docker compose down --remove-orphans
```
<!-- END QUICKSTART -->

---

<!-- START PERSISTENCE -->
## Persistence

All persistent data is stored under `local-telemetry/data/`:

```text
local-telemetry/data/
  collector/
  prometheus/
  loki/
  tempo/
  grafana/
```

This path is ignored by Git:

```text
local-telemetry/data/
```

To delete all locally collected telemetry data:

```bash
rm -rf local-telemetry/data/*
```

Some files may be created as `root` inside `local-telemetry/data/` because the containers
run with `user: "0:0"` to avoid local permission issues with bind mounts.
<!-- END PERSISTENCE -->

---

<!-- START INSTRUMENTATION -->
## Instrumentation

The stack accepts OTLP from any local process that can export OpenTelemetry signals.

Recommended environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_SERVICE_NAME=mcp-experto-filesystem
export OTEL_RESOURCE_ATTRIBUTES=deployment.environment.name=local,service.namespace=expertostech
```

Useful resource and semantic attributes:

* `service.name`
* `service.namespace`
* `service.instance.id`
* `session.id`
* `tool.name`
* `operation.name`
* `gen_ai.system`
* `gen_ai.request.model`
* `gen_ai.usage.input_tokens`
* `gen_ai.usage.output_tokens`
* `gen_ai.usage.total_tokens`

If your CLI or application does not emit model usage metrics yet, the stack still works for:

* traces
* logs
* generic OTLP metrics
* collector health and queue visibility

The fallback path is standard OTLP configuration through process environment variables.
<!-- END INSTRUMENTATION -->

---

<!-- START TROUBLESHOOTING -->
## Troubleshooting

Check the merged Compose configuration:

```bash
cd local-telemetry
docker compose config
```

Check running containers:

```bash
docker compose ps
```

Follow collector logs:

```bash
docker compose logs -f otel-collector
```

Follow Grafana logs:

```bash
docker compose logs -f grafana
```

Open Prometheus directly for metric inspection:

```bash
open http://127.0.0.1:9090
```

If logs do not appear in Loki:

* verify the emitting process is sending OTLP logs, not only traces
* verify the process points to `127.0.0.1:4318` or `127.0.0.1:4317`
* inspect `otel-collector` logs for exporter queue or retry errors

If model usage panels stay empty:

* confirm the CLI or SDK emits GenAI telemetry attributes
* confirm token or cost data is exported as metrics, logs, or trace attributes
* use generic logs and traces first, then refine instrumentation if needed
<!-- END TROUBLESHOOTING -->
