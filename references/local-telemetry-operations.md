<!-- AGENTS SUMMARY
Operational guide for the local telemetry stack used to observe the MCP, its CLI,
and model usage signals when they are emitted.
Sessions:
- TLDR: Fast operational summary of the telemetry stack.
- OVERVIEW: Purpose and scope of the stack.
- QUICKSTART: Startup and shutdown commands.
- PERSISTENCE: Local storage layout and cleanup guidance.
- INSTRUMENTATION: OTLP environment variables and telemetry conventions.
- CLI-MATRIX: Official telemetry signal matrix for each supported CLI.
- DASHBOARDS: Dashboard files provisioned for per-CLI and cross-CLI analysis.
- TROUBLESHOOTING: Common local issues and checks.
- CURL-VALIDATION: Direct local query validation workflow for Prometheus, Loki, and Tempo.
-->

# Local Telemetry Operations

## Table of Contents

* [Overview](#overview)
* [Quickstart](#quickstart)
* [Persistence](#persistence)
* [Instrumentation](#instrumentation)
* [CLI OTel Matrix](#cli-otel-matrix)
* [Dashboards](#dashboards)
* [Troubleshooting](#troubleshooting)
* [Curl Validation](#curl-validation)

---

<!-- START TLDR -->
## TL;DR

* This guide explains how to run the local OTLP, Prometheus, Loki, Tempo, and Grafana stack under `local-telemetry/`.
* The stack is meant to observe the MCP, the host CLI, and model usage signals when those signals are emitted.
* Use it for startup, OTLP wiring, persistence layout, and local troubleshooting.
<!-- END TLDR -->

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

For multiple local CLIs, keep common OTEL variables global and set `OTEL_SERVICE_NAME`
per command through wrappers in `~/.local/bin`:

```bash
otel-copilot
otel-gemini
otel-codex
otel-claude
```

Each wrapper should export a CLI-specific service name before launching the command:

```bash
#!/usr/bin/env sh
set -eu

export OTEL_EXPORTER_OTLP_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT:-http://127.0.0.1:4318}"
export OTEL_EXPORTER_OTLP_PROTOCOL="${OTEL_EXPORTER_OTLP_PROTOCOL:-http/protobuf}"
export OTEL_RESOURCE_ATTRIBUTES="${OTEL_RESOURCE_ATTRIBUTES:-deployment.environment.name=local,service.namespace=expertostech}"
export OTEL_SERVICE_NAME="codex-cli"

exec codex "$@"
```

Use distinct values such as `copilot-cli`, `gemini-cli`, `codex-cli`, and `claude-cli`
to separate signals in Grafana and Tempo.

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

<!-- START CLI-MATRIX -->
## CLI OTel Matrix

The local stack documents and targets four CLI services:

* `copilot-cli`
* `gemini-cli`
* `codex-cli`
* `claude-cli`

Signal support and notable attributes from official references:

| CLI | Signals exported | Notable attributes and notes | Official reference |
| :--- | :--- | :--- | :--- |
| Copilot CLI (via Copilot SDK) | Traces (OTLP HTTP), trace context propagation | `traceparent` / `tracestate` propagation between host app and CLI spans. Telemetry is opt-in via `TelemetryConfig`. | https://docs.github.com/en/copilot/how-tos/copilot-sdk/observability/opentelemetry |
| Gemini CLI | Logs, metrics, traces | Includes common attributes such as `session.id`; exposes rich tool/model/token events and GenAI usage fields. | https://geminicli.com/docs/cli/telemetry/ |
| Codex CLI | Logs, traces, metrics | Open-source OTEL provider shows dedicated logger, tracer, and metrics client, all using `service_name` and OTLP exporters. | https://github.com/openai/codex/blob/main/codex-rs/otel/src/provider.rs |
| Claude Code CLI | Metrics, logs/events, optional traces | Metrics and logs/events are configurable through OTEL env vars. Traces are beta and optional. Includes token/tool-related telemetry controls. | https://code.claude.com/docs/en/monitoring-usage |
<!-- END CLI-MATRIX -->

---

<!-- START DASHBOARDS -->
## Dashboards

Grafana provisioning loads all files under `local-telemetry/grafana/dashboards/`.

Dashboard set for CLI observability:

* `operational-overview.json` (collector and stack-wide health)
* `copilot-cli-overview.json`
* `gemini-cli-overview.json`
* `codex-cli-overview.json`
* `claude-cli-overview.json`
* `cli-workbench-overview.json` (generic cross-CLI workbench with a `service` filter)

Per-CLI dashboards focus on:

* metric series presence by `service_name`
* log volume and recent logs in Loki
* trace search by `resource.service.name` in Tempo
<!-- END DASHBOARDS -->

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

---

<!-- START CURL-VALIDATION -->
## Curl Validation

Expose all local query endpoints on host:

* Prometheus: `127.0.0.1:9090`
* Loki: `127.0.0.1:3100`
* Tempo: `127.0.0.1:3200`

Quick readiness checks:

```bash
curl -fsS http://127.0.0.1:9090/-/ready
curl -fsS http://127.0.0.1:3100/ready
curl -fsS http://127.0.0.1:3200/ready
```

Prometheus query validation examples:

Use Prometheus here to validate collector-side ingestion and export flow. Per-CLI
service validation is more reliable through Loki and Tempo because OTLP resource
attributes such as `service.name` are not always ergonomic to query directly in
PromQL.

```bash
curl -GfsS http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=sum by (receiver) (rate(otelcol_receiver_accepted_spans_total[5m]))'

curl -GfsS http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=sum by (receiver) (rate(otelcol_receiver_accepted_metric_points_total[5m]))'
```

Loki query validation examples:

```bash
curl -GfsS http://127.0.0.1:3100/loki/api/v1/query \
  --data-urlencode 'query=sum(count_over_time({service_name="codex-cli"}[5m]))'

curl -GfsS http://127.0.0.1:3100/loki/api/v1/query_range \
  --data-urlencode 'query={service_name="claude-cli"}' \
  --data-urlencode "start=$(date -u -d '15 minutes ago' +%s)000000000" \
  --data-urlencode "end=$(date -u +%s)000000000" \
  --data-urlencode 'limit=100'

curl -GfsS http://127.0.0.1:3100/loki/api/v1/query_range \
  --data-urlencode 'query={job=~".+"}' \
  --data-urlencode "start=$(date -u -d '15 minutes ago' +%s)000000000" \
  --data-urlencode "end=$(date -u +%s)000000000" \
  --data-urlencode 'limit=100'
```

Tempo trace search validation examples:

```bash
curl -GfsS http://127.0.0.1:3200/api/search \
  --data-urlencode 'q={resource.service.name="copilot-cli"}' \
  --data-urlencode 'limit=20'

curl -GfsS http://127.0.0.1:3200/api/search \
  --data-urlencode 'q={resource.service.name=~"gemini-cli|codex-cli|claude-cli"}' \
  --data-urlencode 'limit=20'
```
<!-- END CURL-VALIDATION -->
