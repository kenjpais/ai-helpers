---
name: generate-reliability-md
description: "Generate RELIABILITY.md file for agentic documentation"
trigger: /generate-reliability-md
---

# Generate RELIABILITY.md Skill

## Purpose

Generate the `agentic/RELIABILITY.md` file documenting SLOs, monitoring, observability, and operational procedures.

## Data Sources

- Monitoring code (pkg/metrics/, internal/metrics/)
- Deployment configs (deploy/, k8s/, manifests/)
- SLO/SLI definitions
- Observability setup (Prometheus rules, Grafana dashboards)
- Alert configurations
- Runbooks or documentation

## Content Sections

1. **SLOs and SLIs** - Service level objectives and indicators
2. **Monitoring and Alerting** - Metrics, alerts, dashboards
3. **Common Failure Modes** - Known issues and failure patterns
4. **Incident Response** - Response procedures and escalation
5. **Troubleshooting Guides** - Diagnostic steps
6. **Operational Runbooks** - Standard operating procedures

**Target**: ~250 lines

## Logging

- Skill: generate-reliability-md
- Data sources: monitoring/, deploy/, observability configs
- Lines generated: [count]
