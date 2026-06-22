# HUMMBL Repo Standard

**Status:** draft v0.1
**Steward:** HUMMBL Research Institute
**Approving human:** Reuben Bowlby
**Source of record:** this file in `hummbl-dev/hummbl-governance` (canonical); templates mirrored in `hummbl-dev/.github`.

## 1. Purpose

Define the minimum, prescribed, and optional governance artifacts for every repository under `hummbl-dev`. Each repo is a governed micro-jurisdiction: it declares its identity, authority, doctrine, agent operating contract, receipt requirements, schemas, validators, and source-of-record boundaries.

This standard is **global**: it informs every repo but does not replace repo-local law. Repo constitutions may be stricter than this standard, never weaker.

## 2. Routing doctrine

Models propose. Schemas constrain. Validators decide. Git records. KRINEIA proves. Humans authorize.

- Non-deterministic systems may discover what could be true.
- Deterministic systems decide what becomes durable.
- Humans / constitutions decide authority.
- Git records state.
- KRINEIA proves admission.

Deterministic spine, stochastic muscle.

## 3. Decision authority

| Class | Decides | May admit durable state? |
|-------|---------|--------------------------|
| Deterministic agent | validity (schema, test, hash, naming, presence, lint, gate) | yes, when rule is explicit, input machine-readable, outcome reproducible, jurisdiction held, consequence bounded, output validatable, receipt logged |
| Non-deterministic agent | plausibility (interpret, rank, classify, draft, critique, synthesize) | only provisionally — requires delegated authority, deterministic gate validation, bounded scope, reversibility/low-risk, no self-rule-change, receipt |
| Human | authority | yes |

Canonical rule: deterministic agents decide validity; non-deterministic agents decide plausibility; humans decide authority.

## 4. Required artifact stack

Every active non-fork repo carries this stack. Each file has one job; do not conflate them.

| File | Job | Governs |
|------|-----|---------|
| `README.md` | identity | what this repo is |
| `CONSTITUTION.md` | authority | binding repo law, scope, protected invariants, amendment, receipt-triggering changes, human approval |
| `DOCTRINE.md` | meaning | interpretive framework, thesis, vocabulary, design principles, boundaries, open questions |
| `AGENTS.md` | execution | agent operating contract: read order, allowed/risky/forbidden work, validation, receipts, provider-neutral |
| `KRINEIA.md` | receipts | repo-local receipt/governance manifest: chains, events, trust-root, verification (not the receipt schema itself) |
| `CONTRIBUTING.md` | contribution | how to propose changes |
| `SECURITY.md` | disclosure | vulnerability reporting |
| `LICENSE` | rights | license terms |
| `CHANGELOG.md` | history | released changes |
| `CODEOWNERS` | ownership | review authority per path |
| `hummbl.repo.yaml` | manifest | machine-readable registry atom |
| `_receipts/` | proof | KRINEIA receipt chains |
| `docs/adr/` | decisions | architecture decision records |
| `docs/handoffs/` | continuity | agent/session handoff notes |
| `scripts/validate.*` | gate | deterministic admission validator |

### Conflict precedence (within a repo)

1. Higher-authority operating constitution, if operating locally on that host
2. `CONSTITUTION.md`
3. `KRINEIA.md`
4. `AGENTS.md`
5. Schemas / tests / validators
6. `DOCTRINE.md`
7. `README.md`
8. Other docs

The global operating-environment constitution (e.g. `C:\_governance\OPERATING_ENVIRONMENT_CONSTITUTION.md`) governs the machine and is **not** duplicated into repos. Repo constitutions include a higher-authority reference section only.

## 5. Repo classes and weight

Not every repo carries the same weight. Class determines which artifacts are **required (R)**, **prescribed (P)**, or **optional (O)**.

### 5.1 Spec / governance repos
`krineia`, `base120`, `idp-spec`, `hummbl-governance`, `hummbl-doctrine`, `hummbl-theory`, `baseN`, `mtsmu`, `huaomp`

| Artifact | Weight |
|----------|--------|
| README, CONSTITUTION, DOCTRINE, AGENTS, KRINEIA, CONTRIBUTING, SECURITY, LICENSE, CHANGELOG, CODEOWNERS, hummbl.repo.yaml | R |
| `_receipts/`, `docs/adr/`, `docs/spec/`, `schemas/`, `scripts/validate.*` | R |
| `docs/handoffs/` | P |

### 5.2 Code / library repos
`mcp-server`, `hummbl-agent`, `arbiter`, `founder-mode`, `hummbl-models`, etc.

| Artifact | Weight |
|----------|--------|
| README, CONSTITUTION, AGENTS, KRINEIA, CONTRIBUTING, SECURITY, LICENSE, CHANGELOG, CODEOWNERS, hummbl.repo.yaml | R |
| `tests/`, `scripts/validate.*`, `_receipts/`, `docs/adr/` | R |
| DOCTRINE, `docs/runbooks/`, `docs/handoffs/` | P |

### 5.3 Docs / research repos
`hummbl-bibliography`, `hummbl-papers`, `hummbl-theory`, `whether-book`

| Artifact | Weight |
|----------|--------|
| README, CONSTITUTION, AGENTS, KRINEIA, LICENSE, CHANGELOG, hummbl.repo.yaml | R |
| DOCTRINE, CONTRIBUTING, SECURITY | P |
| `docs/source-policy.md`, `docs/citation-policy.md`, `_receipts/` | R |

### 5.4 Forks / imported upstream repos
`vllm`, `paramiko`, `rich`, `markitdown`, `cli`, `deer-flow`, `awesome-*`, etc.

| Artifact | Weight |
|----------|--------|
| `HUMMBL_FORK.md`, `AGENTS.md`, `KRINEIA.md`, `hummbl.repo.yaml` | R |
| Everything else | O (preserve upstream) |

Fork boundary (canonical text for `HUMMBL_FORK.md`): _This repo is an upstream fork/import. Preserve upstream semantics unless explicitly creating a HUMMBL patch. Do not confuse upstream authority with HUMMBL authority. HUMMBL governance applies only to HUMMBL-authored additions._

### 5.5 Archived repos
Carry whatever they had at archival. No new required work. A `HUMMBL_FORK.md` or minimal `AGENTS.md` is prescribed only if the repo is still referenced as evidence.

## 6. `hummbl.repo.yaml` — manifest

Every active repo carries one. It is the machine-readable registry atom. Schema: see `schemas/hummbl-repo-manifest.schema.json` (companion to this standard). It declares: identity, purpose, authority, governance profile, validation command, and doc paths. It is **not** a receipt and **not** a constitution.

## 7. `KRINEIA.md` — repo-local manifest (not the schema)

`KRINEIA.md` declares how a repo participates in KRINEIA governance: chains, governed events, trust-root mode, allowed/forbidden operators, verification, and what changes require receipts. It does **not** redefine the canonical receipt schema (that lives in `hummbl-dev/krineia/RECEIPT_SCHEMA.md`). Repo-specific data belongs inside receipt `state`, never as new top-level envelope fields.

Allowed first-class chain operators: `append`, `project`, `cut`. Forbidden: `update`, `delete`, `rewrite`, `summarize_and_replace`, `score_and_train`.

A chain can pass hash validation and still fail KRINEIA if the surrounding system violates the five invariants.

## 8. Provider neutrality

Root governance (`CONSTITUTION.md`, `AGENTS.md`, `KRINEIA.md`, `DOCTRINE.md`, `hummbl.repo.yaml`) must be model/provider/vendor neutral. No root governance file may depend on or name a specific provider (Claude, Codex, Devin, Gemini, Cursor, OpenAI, Anthropic, Cognition, Copilot, etc.) as a precondition of authority. Provider-specific guidance lives in adapter docs under `docs/` or `.hummbl/`, never in root governance.

## 9. RepoLM / RepoBit (forward reference)

A repo may declare a tiny local language/grammar/interpreter under `.hummbl/repo-lm/`. RepoLM interprets; validators and authority admit. Authority stack:

```
Git + receipts -> CONSTITUTION.md -> KRINEIA.md -> AGENTS.md -> schemas/tests -> RepoLM
```

RepoLM/RepoBit must never be sovereign. See `docs/standards/REPOLM.md` (to be drafted).

## 10. Validation

Each repo's `scripts/validate.*` is its deterministic admission gate. The standard does not mandate a specific language; it mandates that a deterministic, reproducible validator exists and is named in `hummbl.repo.yaml.validation.command`. Required before merge for spec/governance repos and before release for all.

## 11. Amendment

Changes to this standard require: a PR to `hummbl-dev/hummbl-governance`, an ADR under `docs/adr/`, a KRINEIA receipt, and human approval (Reuben Bowlby). Breaking changes bump the standard version (SemVer) and trigger a fleet re-audit.
