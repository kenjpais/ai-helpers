---
name: generate-security-md
description: "Generate SECURITY.md file for agentic documentation"
trigger: /generate-security-md
---

# Generate SECURITY.md Skill

## Purpose

Generate the `agentic/SECURITY.md` file documenting the security model, threat analysis, and security controls.

## Data Sources

- RBAC configurations (rbac.yaml, role.yaml, clusterrole.yaml)
- Security policies (SecurityContext, PodSecurityPolicy, NetworkPolicy)
- Authentication/authorization code
- Secrets management (sealed-secrets, external-secrets)
- Security scanning results
- SECURITY.md (if exists in root)

## Content Sections

1. **Threat Model** - Attack vectors and security boundaries
2. **Security Controls** - RBAC, network policies, pod security
3. **Authentication & Authorization** - Identity and access management
4. **Secrets Management** - How secrets are handled
5. **Input Validation** - Input sanitization and validation
6. **Security Scanning** - Tools and processes
7. **Incident Response** - Security incident procedures

**Target**: ~280 lines

## Logging

- Skill: generate-security-md
- Data sources: RBAC configs, security policies, auth code
- Lines generated: [count]
