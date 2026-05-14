# HUMMBL Governance — Vendor Directory Entry
# OWASP AI Security Solutions Landscape
# Format: Solutions Landscape vendor template (Q3 2026 cycle)

---

vendor: HUMMBL, LLC
solution: hummbl-governance
website: https://github.com/hummbl-dev/hummbl-governance
contact: reuben@hummbl.io
license: Apache-2.0
version: "0.8.0"
release_date: "2026-05-14"
language: Python (3.11+)
runtime_dependencies: none (stdlib only)
test_count: 927
test_status: all passing
mcp_servers: 7

category: governance-platform
lifecycle_stages:
  - planning
  - development
  - testing
  - deployment
  - operations
  - monitoring

frameworks_mapped:
  - OWASP LLM Top 10 (2025)
  - OWASP Agentic Top 10 (2026)
  - NIST AI RMF 1.0
  - NIST CSF 2.0
  - ISO/IEC 42001
  - ISO/IEC 27001
  - SOC 2
  - GDPR
  - EU AI Act

agentic_coverage:
  excessive_agency: partial
  tool_misuse: partial
  memory_poisoning: partial
  intent_hijacking: partial
  planning_chain_coercion: partial
  insufficient_output_validation: partial
  unsafe_code_execution: none
  dos_resource_exhaustion: full
  supply_chain_vulnerabilities: full
  logging_monitoring_failures: full

key_capabilities:
  - "Kill switch (4-mode graduated halt)"
  - "Circuit breaker (3-state FSM)"
  - "Cost governor (SQLite-backed budgets)"
  - "HMAC-SHA256 delegation tokens"
  - "Append-only audit log (JSONL)"
  - "Agent identity registry + trust scoring"
  - "JSON Schema validation (stdlib)"
  - "7 MCP servers (32+ tools)"
  - "Multi-agent coordination bus"
  - "Content review / output gates"

differentiators:
  - "Zero runtime dependencies — stdlib only"
  - "Embeddable library (not SaaS platform)"
  - "Native MCP integration (7 servers)"
  - "Supply-chain security (zero deps + SBOM)"
  - "Multi-agent peer review protocol (CRAB)"
  - "927 passing tests across 4 Python versions"

gaps:
  - description: "No execution sandboxing"
    severity: HIGH
    mitigation: "Document recommended sandboxes (gVisor, Firecracker)"
  - description: "No semantic output filtering"
    severity: MEDIUM
    mitigation: "Content-safety filter planned Q3 2026"
  - description: "No real-time intent monitoring"
    severity: MEDIUM
    mitigation: "IntentVerifier module planned Q3 2026"

references:
  - title: "OWASP Agentic Top 10 Compliance Mapping"
    url: "https://github.com/hummbl-dev/hummbl-governance/blob/main/docs/OWASP_MAPPING.md"
  - title: "OWASP LLM Top 10 Coverage Matrix"
    url: "https://github.com/hummbl-dev/hummbl-governance/blob/main/docs/coverage/owasp-llm.md"
  - title: "NIST CSF Mapping"
    url: "https://github.com/hummbl-dev/hummbl-governance/blob/main/docs/nist-csf-mapping.md"
  - title: "Full Submission (Q3 2026)"
    url: "https://github.com/hummbl-dev/hummbl-governance/blob/main/docs/submissions/OWASP_SOLUTIONS_LANDSCAPE_Q3_2026.md"