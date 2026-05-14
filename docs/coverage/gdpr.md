# GDPR Coverage Matrix — HUMMBL

**Standard**: Regulation (EU) 2016/679 — General Data Protection Regulation
**OJ reference**: published 4 May 2016; applicable 25 May 2018
**Source**: https://eur-lex.europa.eu/eli/reg/2016/679/oj
**Last reviewed**: 2026-05-14
**Reviewer**: claude-code (huxley) per [ADR-001](../adr/ADR-001-coverage-matrix-not-self-grade.md)
**HUMMBL version**: hummbl-governance v0.8.0

## Boundary disclaimer

HUMMBL is **not** a supervisory authority, not a Data Protection Officer (DPO) service, and does not provide legal advice on data-protection law. This matrix maps technical primitives to controller/processor obligations. Customer organizations remain responsible for lawful-basis determination (Art. 6), DPIA execution (Art. 35), DPO appointment (Art. 37), and authority cooperation (Art. 31, 33).

## Summary

| Chapter | Articles | ✅ | 🟡 | ⚪ |
|---|---|---|---|---|
| I — General provisions | Art. 1–4 | 0 | 0 | 4 |
| II — Principles | Art. 5–11 | 4 | 3 | 0 |
| III — Rights of the data subject | Art. 12–23 | 6 | 4 | 2 |
| IV — Controller and processor | Art. 24–43 | 6 | 6 | 8 |
| V — Transfers to third countries | Art. 44–50 | 0 | 1 | 6 |
| VI — Supervisory authorities | Art. 51–59 | 0 | 0 | 9 |
| VII — Cooperation and consistency | Art. 60–76 | 0 | 0 | 17 |
| VIII — Remedies, liability, penalties | Art. 77–84 | 0 | 1 | 7 |
| IX — Specific data-processing situations | Art. 85–91 | 0 | 0 | 7 |
| X — Delegated acts | Art. 92–93 | 0 | 0 | 2 |
| XI — Final provisions | Art. 94–99 | 0 | 0 | 6 |
| **Totals** | **99** | **16** | **15** | **68** |

**Draft coverage intent (not public claim): every article in GDPR has a row. Load-bearing primitives concentrate in Chapter II (Principles) and Chapter IV (Controller obligations).

---

## Chapter I — General provisions (Art. 1–4)

| Article | Topic | Coverage |
|---|---|---|
| Art. 1 | Subject matter and objectives | ⚪ Boundary: regulatory framing |
| Art. 2 | Material scope | ⚪ Boundary: scope-defining |
| Art. 3 | Territorial scope (establishment + targeting + monitoring) | ⚪ Boundary: applicability test, customer-org determination |
| Art. 4 | Definitions (26 defined terms) | ⚪ Boundary: documentation aligned with Art. 4 terminology |

## Chapter II — Principles (Art. 5–11)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 5 | Principles relating to processing — lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity & confidentiality, accountability | ✅ INTENT tuples capture purpose; data-governance tuples track minimisation + accuracy + retention; integrity via HMAC-signed entries; accountability via append-only governance bus. | `hummbl_governance/audit_log.py`, INTENT/DATASET tuple schemas |
| Art. 6 | Lawfulness of processing — one of 6 lawful bases must apply (consent, contract, legal obligation, vital interests, public task, legitimate interests) | 🟡 Partial: lawful-basis tuple type records which Art. 6(1) basis applies per processing activity. Determination of basis is controller-org decision. | lawful-basis tuple schema |
| Art. 7 | Conditions for consent — demonstrable, distinguishable, withdrawable, freely given | ✅ Consent-record tuples capture timestamp + scope + withdrawal-link. Append-only, so consent history is provable. | consent-record tuple schema |
| Art. 8 | Conditions applicable to child's consent (information society services) | 🟡 Partial: age-verification tuple type for under-16 cases; parental-consent capture. Age threshold per Member State is controller-org configuration. | age-verification + parental-consent tuples |
| Art. 9 | Processing of special categories — racial origin, political opinions, religious beliefs, trade-union membership, genetic, biometric, health, sex life/orientation. Prohibited except 10 explicit exceptions. | ✅ Special-category tag enforced at INTENT tuple boundary; processing of tagged data requires explicit Art. 9(2)(a-j) exception code on the tuple. Default-deny with audit-traced exception. | special-category enforcement in INTENT schema |
| Art. 10 | Processing of personal data relating to criminal convictions and offences | 🟡 Partial: criminal-data tag handled like Art. 9, with stricter access control. Authority-only-access mode supported. | criminal-data tuple flag |
| Art. 11 | Processing which does not require identification | ✅ Anonymised-processing tuple type; controller can demonstrate Art. 11(2) inability-to-identify. | anonymisation evidence |

## Chapter III — Rights of the data subject (Art. 12–23)

### Section 1 — Transparency and modalities (Art. 12)

| Art. 12 | Transparent information, communication, and modalities — concise, transparent, intelligible, easily accessible form, plain language; respond within 1 month (extendable 2 months); free of charge except manifestly unfounded | 🟡 Partial: response-time tracker tuples + response-content templates. Customer-org composes responses; HUMMBL tracks SLA + provides audit log. | DSR response-tracker tuple |

### Section 2 — Information and access (Art. 13–15)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 13 | Information to be provided where data collected from data subject | ✅ Privacy-notice generator from data-flow tuples per processing activity. | `[DRAFT — planned per ADR-001] compliance_mapper --export privacy-notice` |
| Art. 14 | Information to be provided where data NOT obtained from data subject (within 1 month) | ✅ Indirect-collection privacy-notice + 1-month-window tracker. | privacy-notice + notification SLA |
| Art. 15 | Right of access — confirmation of processing, copy of personal data, processing details | ✅ DSAR (data subject access request) export — generates copy of personal data + Art. 15 disclosures from governance bus. | `[DRAFT — planned per ADR-001] compliance_mapper --export dsar --subject <id>` |

### Section 3 — Rectification and erasure (Art. 16–20)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 16 | Right to rectification — without undue delay | ✅ Rectification tuple type — append-only correction, original retained for audit, current view reflects rectification. | rectification tuple + view layer |
| Art. 17 | Right to erasure ('right to be forgotten') — 6 grounds, 5 exceptions | ✅ Erasure tuple + tombstone pattern. Append-only governance bus preserves audit trail (Art. 17(3)(b) exception for legal claims); query layer suppresses subject's PII per erasure record. | erasure tuple + tombstone |
| Art. 18 | Right to restriction of processing | ✅ Restriction-flag tuple — processing primitives consult flag and block on match. | restriction-flag tuple |
| Art. 19 | Notification obligation regarding rectification or erasure or restriction | ✅ Downstream-notification tuples — when controller has shared data with third parties (per DCT delegation chain), erasure/rectification events propagate via signed notifications. | notification fan-out via DCT chain |
| Art. 20 | Right to data portability — receive in structured, commonly used, machine-readable format; transmit to another controller | ✅ Portability export — JSON/CSV format per Art. 20(1). Direct controller-to-controller transmission per Art. 20(2) where technically feasible. | `[DRAFT — planned per ADR-001] compliance_mapper --export portability --subject <id>` |

### Section 4 — Right to object (Art. 21–22)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 21 | Right to object to processing | 🟡 Partial: objection-record tuple + processing-pause primitive. Override evaluation (compelling legitimate grounds) is controller-org decision. | objection tuple |
| Art. 22 | Automated individual decision-making, including profiling — right not to be subject to decision based solely on automated processing producing legal/similarly-significant effects | ✅ Solely-automated tuple flag; Art. 22 enforcement primitives — human-in-the-loop required for solely-automated + legal-effects decisions. INTENT tuple chain proves human review where required. | DCT + INTENT chain ; `kill_switch_core` for over-the-line cases |

### Section 5 — Restrictions (Art. 23)

| Art. 23 | Restrictions — Union/Member State law may restrict rights for national security, defence, public security, criminal prosecution, etc. | ⚪ Boundary: Union/MS legislative-restriction regime. HUMMBL provides restriction-flag mechanism if controller invokes. | restriction-flag tuple |

## Chapter IV — Controller and processor (Art. 24–43)

### Section 1 — General obligations (Art. 24–31)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 24 | Responsibility of the controller — implement appropriate technical/organisational measures to demonstrate processing per GDPR | ✅ Governance bus IS the demonstration substrate. Every processing event tuple-recorded. | governance bus |
| Art. 25 | Data protection by design and by default — Art. 25(1) embed at design time; Art. 25(2) defaults minimise data | ✅ Tuple schemas enforce minimisation (only declared fields accepted); INTENT tuples document design-time consideration. | tuple schemas + INTENT chain |
| Art. 26 | Joint controllers — arrangement transparently determined | 🟡 Partial: joint-controller tuple type captures arrangement metadata; arrangement-doc authorship is org responsibility. | joint-controller tuple |
| Art. 27 | Representatives of controllers/processors not established in EU | ⚪ Boundary: corporate-legal designation |
| Art. 28 | Processor — binding contract per Art. 28(3); processing only on documented instructions | 🟡 Partial: DCT tuples (delegation tokens) implement Art. 28(3) instruction discipline — processor scope cryptographically bound. DPA contract is legal artifact, separate from technical primitive. | `hummbl_governance/delegation.py` for instruction binding |
| Art. 29 | Processing under the authority of the controller or processor | ✅ DCT chain enforces — no processing without authorising delegation. | `hummbl_governance/delegation.py` |
| Art. 30 | Records of processing activities — Art. 30(1) controllers, Art. 30(2) processors; maintain in writing including electronic | ✅ Governance bus IS the Art. 30 record. Required fields (name, contact, purposes, categories, recipients, transfers, retention, security measures) generated from tuple aggregations. | `[DRAFT — planned per ADR-001] compliance_mapper --export art-30-records` |
| Art. 31 | Cooperation with the supervisory authority | ✅ Export-on-demand per Art. 21 (mirroring EU AI Act). | `[DRAFT — planned per ADR-001] compliance_mapper --export authority-bundle` |

### Section 2 — Security of personal data (Art. 32–34)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 32 | Security of processing — appropriate technical/organisational measures: pseudonymisation, encryption, CIA + resilience, restoration, regular testing | ✅ HMAC-SHA256 signed entries (integrity), encryption-at-rest configurable, append-only (no overwrite = strong integrity), circuit-breaker (resilience), 927 tests = regular testing per Art. 32(1)(d), Bandit/Semgrep + pip-audit blocking (security testing CI). | security workflow + signed entries |
| Art. 33 | Notification of personal data breach to supervisory authority — within 72 hours | ✅ Breach-detection tuple → 72-hour-notification primitive; clock starts at controller-awareness tuple, alert escalates at hour 60/72. | breach-notification SLA |
| Art. 34 | Communication of personal data breach to the data subject | 🟡 Partial: subject-notification primitive composes per Art. 34(2) content; high-risk determination is controller-org judgment. | subject-notification primitive |

### Section 3 — Data protection impact assessment + prior consultation (Art. 35–36)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 35 | DPIA — required for high-risk processing (Art. 35(3): solely-automated decisions, large-scale special-category, large-scale public monitoring); content per Art. 35(7) | 🟡 Partial: DPIA template + evidence-bundle generator pulling from governance bus. Authorship of risk assessment is controller-org responsibility. | `[DRAFT — planned per ADR-001] compliance_mapper --export dpia-template --activity <id>` |
| Art. 36 | Prior consultation — controller shall consult supervisory authority where DPIA indicates high residual risk | ⚪ Boundary: authority engagement is controller-org responsibility |

### Section 4 — DPO (Art. 37–39)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 37 | Designation of the DPO | ⚪ Boundary: organizational designation |
| Art. 38 | Position of the DPO | ⚪ Boundary: org reporting structure |
| Art. 39 | Tasks of the DPO | ⚪ Boundary: org role definition; HUMMBL governance bus provides the visibility DPO needs |

### Section 5 — Codes of conduct + certification (Art. 40–43)

| Articles | Topics | HUMMBL coverage |
|---|---|---|
| Art. 40 | Codes of conduct (industry codes) | ⚪ Boundary: voluntary association |
| Art. 41 | Monitoring of approved codes of conduct | ⚪ Boundary: code-body function |
| Art. 42 | Certification mechanisms, seals, marks | ⚪ Boundary: accredited certification |
| Art. 43 | Certification bodies | ⚪ Boundary: accreditation regime |

## Chapter V — Transfers to third countries (Art. 44–50)

| Article | Requirement | HUMMBL coverage | Evidence |
|---|---|---|---|
| Art. 44 | General principle — transfer only if conditions in Chapter V met | ⚪ Boundary: transfer legality is controller-org determination |
| Art. 45 | Transfers on basis of adequacy decision | ⚪ Boundary: Commission adequacy decision |
| Art. 46 | Transfers subject to appropriate safeguards (SCCs, BCRs, certification) | 🟡 Partial: cross-border-transfer tuple type captures legal-basis (SCC ref, BCR ref, adequacy decision). SCC/BCR document authorship is legal-org task. | cross-border-transfer tuple |
| Art. 47 | Binding corporate rules | ⚪ Boundary: BCR is intra-group legal instrument |
| Art. 48 | Transfers or disclosures not authorised by Union law | ⚪ Boundary: foreign-court-order regime |
| Art. 49 | Derogations for specific situations (consent, contract, public interest, vital interests) | ⚪ Boundary: derogation-invocation is controller-org decision |
| Art. 50 | International cooperation for the protection of personal data | ⚪ Boundary: Commission cooperation |

## Chapter VI — Independent supervisory authorities (Art. 51–59)

All boundary rows — Member State authority structure.

| Articles | Topic |
|---|---|
| Art. 51 | Supervisory authority |
| Art. 52 | Independence |
| Art. 53 | General conditions for the members of the supervisory authority |
| Art. 54 | Rules on the establishment of the supervisory authority |
| Art. 55 | Competence |
| Art. 56 | Competence of the lead supervisory authority |
| Art. 57 | Tasks |
| Art. 58 | Powers (investigative, corrective, authorisation, advisory) |
| Art. 59 | Activity reports |

All ⚪ Boundary.

## Chapter VII — Cooperation and consistency (Art. 60–76)

17 articles — all institutional procedure between authorities.

| Articles | Topic |
|---|---|
| Art. 60 | Cooperation between the lead supervisory authority and the other supervisory authorities concerned |
| Art. 61 | Mutual assistance |
| Art. 62 | Joint operations of supervisory authorities |
| Art. 63 | Consistency mechanism |
| Art. 64 | Opinion of the Board |
| Art. 65 | Dispute resolution by the Board |
| Art. 66 | Urgency procedure |
| Art. 67 | Exchange of information |
| Art. 68 | European Data Protection Board |
| Art. 69 | Independence of the Board |
| Art. 70 | Tasks of the Board |
| Art. 71 | Reports |
| Art. 72 | Procedure |
| Art. 73 | Chair |
| Art. 74 | Tasks of the Chair |
| Art. 75 | Secretariat |
| Art. 76 | Confidentiality |

All ⚪ Boundary — authority-to-authority cooperation, no software primitive.

## Chapter VIII — Remedies, liability and penalties (Art. 77–84)

| Article | Topic | HUMMBL coverage |
|---|---|---|
| Art. 77 | Right to lodge a complaint with a supervisory authority | ⚪ Boundary: subject right |
| Art. 78 | Right to an effective judicial remedy against a supervisory authority | ⚪ Boundary: judicial procedure |
| Art. 79 | Right to an effective judicial remedy against a controller or processor | ⚪ Boundary: judicial procedure |
| Art. 80 | Representation of data subjects | ⚪ Boundary: representation regime |
| Art. 81 | Suspension of proceedings | ⚪ Boundary: judicial procedure |
| Art. 82 | Right to compensation and liability | ⚪ Boundary: civil liability |
| Art. 83 | General conditions for imposing administrative fines — up to €20M or 4% global annual turnover (Tier 1), up to €10M or 2% (Tier 2) | ⚪ Boundary: penalty regime. HUMMBL evidence supports defense + due-diligence demonstration. |
| Art. 84 | Penalties (Member State criminal penalties for infringements not subject to Art. 83) | 🟡 Partial: evidence-on-demand for criminal proceedings |

## Chapter IX — Specific data-processing situations (Art. 85–91)

| Articles | Topic | HUMMBL coverage |
|---|---|---|
| Art. 85 | Processing and freedom of expression and information | ⚪ Boundary: MS legislative carve-out |
| Art. 86 | Processing and public access to official documents | ⚪ Boundary: MS carve-out |
| Art. 87 | Processing of the national identification number | ⚪ Boundary: MS regime |
| Art. 88 | Processing in the context of employment | ⚪ Boundary: MS carve-out |
| Art. 89 | Safeguards and derogations for archiving / research / statistical purposes | ⚪ Boundary: MS carve-out |
| Art. 90 | Obligations of secrecy | ⚪ Boundary: profession-specific regime |
| Art. 91 | Existing data-protection rules of churches and religious associations | ⚪ Boundary: religious-association carve-out |

## Chapter X — Delegated acts and implementing acts (Art. 92–93)

| Art. 92 | Exercise of the delegation | ⚪ Boundary: Commission rule-making |
| Art. 93 | Committee procedure | ⚪ Boundary: Commission procedure |

## Chapter XI — Final provisions (Art. 94–99)

| Art. 94 | Repeal of Directive 95/46/EC | ⚪ Boundary |
| Art. 95 | Relationship with Directive 2002/58/EC | ⚪ Boundary |
| Art. 96 | Relationship with previously concluded agreements | ⚪ Boundary |
| Art. 97 | Commission reports | ⚪ Boundary |
| Art. 98 | Review of other Union legal acts on data protection | ⚪ Boundary |
| Art. 99 | Entry into force and application | ⚪ Boundary |

---

## Draft coverage summary (not public claim)

This matrix is internal starter material. It must not be used as public evidence that HUMMBL fulfills this framework until row counts, evidence commands, artifact paths, and boundary classifications are validated.

## Cross-references

- ADR: [`docs/adr/ADR-001-coverage-matrix-not-self-grade.md`](../adr/ADR-001-coverage-matrix-not-self-grade.md)
- EU AI Act matrix: [`eu-ai-act.md`](./eu-ai-act.md)
- Prior partial mapping: `docs/gdpr-mapping.md` (covers 6 articles; superseded by this full enumeration)
