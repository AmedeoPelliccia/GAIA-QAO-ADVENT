# GAI-A Tree Specification v1.0

**Status: LOCKED** — Definitions, layer assignments, and tree rules are final.

> *Everything built so far — AMPEL360, OPT-IN, WMCAA, IDEALE, MUSIC-MCC — becomes a leaf or branch in a single tree.*

---

## 1. Tree Overview

```
L0  ── GAI-A council
       │
L1  ── AMAR board
       │
L2  ── AGGIX core
       │
       ├──────────────┬──────────────┬──────────────┐
L3a    AMPEL        L3b MARE-E     L3c GAIR-SPACE  L3d Robotics A+
       Aerospace         Marine         Space+QC        Autonomous
       │                 │              │               │ (multi-parent)
       ├─────────────────┴──────────────┴───────────────┤
L4  ── Assembly lines (cross-domain modular assemblies)
       │
L5  ── Programs and products
       (AMPEL360 Q100, GAIA-SPACE-LAUNCHER, SPACET Q10, ARES-X, …)
```

---

## 2. Locked Acronyms

| Acronym | Full Expansion | Layer | Role |
|---------|----------------|-------|------|
| **GAI-A** | **G**aia-**A**ligned **I**ntelligence **A**rchitecture | L0 (root) | Immutable principles council |
| **AMAR** | **A**rchitectural **M**ission **A**uthority and **R**oadmap | L1 (trunk) | Portfolio, funding, cross-domain strategy |
| **AGGIX** | **Agg**regation + **G**lobal **I**nfrastructure E**x**change | L2 (trunk) | Global abstract internet, registries, exchange |
| **AMPEL** | **A**erospace **M**odel for **P**roduct and **E**ngineering **L**ifecycles | L3a (branch) | Aerospace domain |
| **MARE-E** | **Mar**itime **E**ngineering **E**cosystem | L3b (branch) | Maritime domain |
| **GAIR-SPACE** | **GAIA** **Air**-**Space** **S**ystems | L3c (branch) | Space + quantum domain (QAOS, NBT, GAIA constellation, launch) |
| **Robotics A+** | **A**utonomous (A) + Augmented/cross-domain (+) | L3d (cross-cutting) | UAVs, swarms, marine autonomous platforms, orbital robotics |

### Robotics A+ — multi-parent semantics

Robotics A+ is the cross-cutting branch for autonomous systems.  Its assemblies inherit the constraints of **every** branch they serve.  The "A+" means **autonomy + augmentation cross-domain**.  A UAV swarm serving both AMPEL (aerospace) and MARE-E (marine) simultaneously carries the union of both branches' certification requirements.

---

## 3. Layer Definitions

### L0 — GAI-A Council (Root)

The root of the tree.  Immutable principles that every downstream layer inherits and cannot override:

- **Data sovereignty** — no silent exfiltration, consent-first
- **Sustainability baseline** — circularity, climate accounting, Digital Product Passport (DPP)
- **Multilingual parity** — no English-only lock-in
- **Human-in-the-loop** — for safety-critical decisions
- **Open evidence, governed inference**

**Standards:**
`Gaia-X Trust Framework` · `EU Data Act` · `EU AI Act` · `GDPR sovereignty clauses` · `ISO 14001 (env)` · `ISO 26000 (social)`

**Tree rule:** L0 principles propagate by inheritance to all descendants.  No branch or leaf may weaken an L0 constraint.  Strengthening is permitted.

---

### L1 — AMAR Board (Trunk)

Portfolio governance, funding allocation, and cross-domain strategic decisions.

**Responsibilities:**
- Approve new L3 branch creation or deprecation
- Allocate budget across branches
- Resolve cross-branch resource conflicts
- Set programme milestones and readiness gates

**Standards:**
`ISO 21500 (project mgmt)` · `ISO 55000 (asset mgmt)` · `PRINCE2 / PMBoK`

---

### L2 — AGGIX Core (Trunk)

The global abstract internet: registries, resource exchange, and interaction protocols that all branches share.

**Standards:**
`ISO 27001 (info security)` · `ISO 20000-1 (IT service mgmt)` · `W3C DID / Verifiable Credentials` · `OGC (geospatial)` · `STIX/TAXII (threat intel)`

---

### L3a — AMPEL (Branch: Aerospace)

Aerospace Model for Product and Engineering Lifecycles.

**Sub-structures mapping:**
- **OPT-IN** → AMPEL's internal optimisation structure
- **WMCAA** → AMPEL sub-branch with L/D assemblies
- **MUSIC-MCC** → AMPEL ATA 46-50

**Standards:**
`DO-178C (sw airborne)` · `DO-254 (hw airborne)` · `ARP4754A (dev processes)` · `ARP4761A (safety)` · `EASA CS-25` · `FAA 14 CFR Part 25` · `S1000D` · `S3000L`

---

### L3b — MARE-E (Branch: Marine)

Maritime Engineering Ecosystem.

**Standards:**
`IEC 61508 (functional safety)` · `IMO SOLAS` · `DNV-GL rules` · `ISO 19847/19848 (ship data)` · `IACS UR`

---

### L3c — GAIR-SPACE (Branch: Space + Quantum)

GAIA Air-Space Systems: QAOS quantum platforms, next-gen broadband telecom (NBT), GAIA constellation operations, launch systems.

**Standards:**
`ECSS-E-ST (space engineering)` · `ECSS-Q-ST (space quality)` · `NASA-STD-8719 (safety)` · `CCSDS (data/comms)` · `ITU Radio Regulations`

---

### L3d — Robotics A+ (Cross-cutting)

Autonomous + Augmented/cross-domain systems.  Multi-parent: assemblies inherit constraints from each branch they serve.

**Standards:**
`ISO 10218 (industrial robots)` · `ISO 13482 (service robots)` · `ISO 22166 (robotics safety)` · `DO-365 (UAV type cert)` · `STANAG 4586 (UAV interop)`

---

### L4 — Assembly Lines

Cross-domain modular assemblies.  Each assembly line instantiates a branch template and may serve multiple L3 parents.

**Standards:**
`AS9100D (aerospace quality)` · `ISO 9001 (general quality)` · `ISO 3834 (welding)` · `NADCAP (special processes)` · `ISO 14644 (cleanrooms)`

---

### L5 — Programs and Products

Concrete programmes and deliverables:
- **AMPEL360 Q100** — next-gen blended wing body aircraft
- **GAIA-SPACE-LAUNCHER** — reusable orbital launcher
- **SPACET Q10** — quantum satellite constellation
- **ARES-X** — autonomous exploration platform

---

## 4. The 8 Tree Rules

These rules govern how constraints, certifications, and resources flow through the tree:

### Rule 1: Downward Propagation
Every constraint defined at layer *N* is automatically inherited by all layers *N+1, N+2, …* in its subtree.  A child node never needs to re-declare a parent constraint.

### Rule 2: Monotonic Strengthening
A child may **strengthen** (tighten) an inherited constraint but may **never weaken** it.  Example: L0 requires "human-in-the-loop for safety-critical"; an L3a assembly may require "two-person-rule for flight-critical" — this is a valid strengthening.

### Rule 3: Multi-Parent Union
When an assembly serves multiple branches (e.g., Robotics A+ serving AMPEL and MARE-E), its effective constraint set is the **union** of all parent constraints.  Where two constraints address the same property, the **strictest** wins.

### Rule 4: Upward Certification
Certification evidence flows **upward**.  A leaf's compliance proof is aggregated at the assembly (L4), then at the branch (L3), then at AGGIX (L2) for cross-branch visibility.  No layer may claim certification its children have not demonstrated.

### Rule 5: AMAR Branching Approval
New L3 branches may only be created with **AMAR board approval** (L1).  Branch creation requires a charter documenting scope, standards mapping, and resource allocation.

### Rule 6: Branch Template Instantiation
Every assembly line (L4) must be instantiated from a **registered branch template**.  The template defines the minimum constraint set, required standards, and interface contracts.

### Rule 7: Durability (No Deletion — Only Deprecation)
No node in the tree may be deleted.  Nodes that are no longer active are marked `DEPRECATED` with a timestamp and successor reference.  Historical traceability is preserved indefinitely.

### Rule 8: Reuse (No Copy — Only Linking)
When a resource (assembly, specification, standard) is needed in multiple branches, it is **linked** via AGGIX URI — never copied.  A single canonical version exists; consumers reference it by URI with version pinning.

---

## 5. Strictest-Wins Resolution

When cross-domain conflicts arise (e.g., an H₂ PEM fuel cell stack serving both AMPEL aerospace and MARE-E maritime), the resolution rule is:

> **The strictest standard wins.**  The assembly carries **both** certifications simultaneously.

| Conflict Scenario | AMPEL Requires | MARE-E Requires | Resolution |
|---|---|---|---|
| Software safety | DO-178C DAL-A | IEC 61508 SIL-4 | Both — dual certification |
| Environmental | ISO 14001 + DPP | ISO 14001 + IMO MARPOL | Union: ISO 14001 + DPP + IMO MARPOL |
| Quality system | AS9100D | DNV-GL Type Approval | Both — dual audit |

---

## 6. AGGIX Resource Model

### 6.1 Resource Types (10)

| Code | Resource Type | Description |
|------|--------------|-------------|
| `ASM` | Assembly | Modular hardware/software assembly |
| `SPC` | Specification | Technical specification document |
| `STD` | Standard | Regulatory or industry standard reference |
| `CRT` | Certificate | Compliance/certification evidence |
| `TT` | Technology Transfer | Cross-branch technology transfer record |
| `DPP` | Digital Product Passport | Sustainability and lifecycle data |
| `AGT` | Agent | Autonomous agent or AI model registration |
| `GRD` | Grid | Physical infrastructure (GAIA Grids) |
| `PRG` | Programme | L5 programme or product registration |
| `TPL` | Template | Branch template for assembly instantiation |

### 6.2 Canonical URI Scheme

```
aggix://{domain}/{branch}/{programme}/{type}/{id}@{version}
```

**Examples:**
```
aggix://gaia/ampel/q100/ASM/wing-box-001@3.2.1
aggix://gaia/mare-e/poseidon/ASM/hull-sensor-array@1.0.0
aggix://gaia/gair-space/spacet-q10/CRT/ecss-e-st-40@2.1.0
aggix://gaia/robotics-a+/swarm-uav/AGT/swarm-controller@4.0.0
aggix://gaia/aggix/core/STD/iso-27001-2022@1.0.0
```

### 6.3 Interaction Verbs (7)

| Verb | Description | Policy Gate |
|------|-------------|-------------|
| `CREATE` | Register a new resource in the AGGIX registry | Branch template validation + L1 budget check |
| `READ` | Retrieve resource metadata or content | Access control (sovereignty-aware) |
| `UPDATE` | Modify a resource (creates new version) | Changelog + backward-compatibility check |
| `LINK` | Create a cross-branch reference to an existing resource | Multi-parent union constraint verification |
| `CERTIFY` | Attach certification evidence to a resource | Upward certification rule (Rule 4) |
| `TRANSFER` | Move a resource between branches (via TT record) | AMAR approval + constraint compatibility |
| `DEPRECATE` | Mark a resource as deprecated (Rule 7) | Successor reference required |

---

## 7. Existing Component Mapping

All existing GAIA-QAO-ADVENT components map into the tree:

| Existing Component | Tree Position | Mapping |
|---|---|---|
| **IDEALE** | L2 → L3a | Framework becomes the AGGIX↔AMPEL interface |
| **OPT-IN** | L3a (internal) | AMPEL's internal optimisation structure |
| **PATH→MTL** | L2 (interaction) | An AGGIX interaction pattern (TRANSFER verb) |
| **TT** (Technology Transfer) | L2 (resource) | An AGGIX resource type (`TT`) |
| **WMCAA** | L3a (sub-branch) | AMPEL sub-branch with L/D assemblies |
| **MUSIC-MCC** | L3a (ATA 46-50) | Lives under AMPEL, ATA chapters 46-50 |
| **GAIA Grids** | L2 (physical) | AGGIX's physical realisation (`GRD` resource type) |
| **AMPEL360** | L5 (product) | Programme under AMPEL branch |
| **QAOS** | L3c (platform) | GAIR-SPACE quantum platform |
| **SICOCA** | L2 (execution) | AGGIX circuit orchestration for chain interlocking |

---

## 8. Standards Master List (by Layer)

### L0 — GAI-A (Root Principles)
1. Gaia-X Trust Framework
2. EU Data Act (2023/2854)
3. EU AI Act (2024/1689)
4. GDPR — sovereignty clauses (Art. 44-49)
5. ISO 14001 — Environmental Management
6. ISO 26000 — Social Responsibility

### L1 — AMAR (Governance)
7. ISO 21500 — Project Management
8. ISO 55000 — Asset Management
9. PRINCE2 / PMBoK

### L2 — AGGIX (Infrastructure)
10. ISO 27001 — Information Security
11. ISO 20000-1 — IT Service Management
12. W3C DID — Decentralized Identifiers
13. W3C Verifiable Credentials
14. OGC Standards — Geospatial
15. STIX/TAXII — Threat Intelligence

### L3a — AMPEL (Aerospace)
16. DO-178C — Software Considerations in Airborne Systems
17. DO-254 — Design Assurance for Airborne Electronic Hardware
18. DO-326A / DO-356A — Airworthiness Security
19. ARP4754A — Development of Civil Aircraft and Systems
20. ARP4761A — Safety Assessment Process
21. EASA CS-25 — Large Aeroplanes
22. FAA 14 CFR Part 25 — Airworthiness Standards
23. S1000D — Technical Publications
24. S3000L — Logistics Support Analysis
25. S5000F — In-Service Data Feedback
26. ATA iSpec 2200 — Chapter structure
27. MSG-3 — Maintenance Program Development

### L3b — MARE-E (Marine)
28. IEC 61508 — Functional Safety
29. IMO SOLAS — Safety of Life at Sea
30. IMO MARPOL — Marine Pollution Prevention
31. DNV-GL Classification Rules
32. ISO 19847 / 19848 — Ship Data
33. IACS Unified Requirements
34. IEC 62443 — Industrial Cybersecurity

### L3c — GAIR-SPACE (Space)
35. ECSS-E-ST — Space Engineering Standards
36. ECSS-Q-ST — Space Product Assurance
37. ECSS-M-ST — Space Management Standards
38. NASA-STD-8719 — Safety Standard
39. CCSDS — Consultative Committee for Space Data Systems
40. ITU Radio Regulations
41. UN COPUOS Guidelines — Space Debris Mitigation

### L3d — Robotics A+ (Autonomous)
42. ISO 10218 — Industrial Robots Safety
43. ISO 13482 — Personal Care Robots Safety
44. ISO 22166 — Robotics Safety Design
45. DO-365 — UAV Type Certification
46. STANAG 4586 — UAV Interoperability
47. IEEE 1872 — Ontologies for Robotics

### L4 — Assembly Lines
48. AS9100D — Aerospace Quality Management
49. ISO 9001 — General Quality Management
50. ISO 3834 — Welding Quality
51. NADCAP — Special Processes Accreditation
52. ISO 14644 — Cleanrooms and Controlled Environments

### L5 — Programs (inherit all parent standards)
53. Programme-specific certification plans
54. Type Certificate Data Sheets (TCDS)
55. Supplemental Type Certificates (STC)

---

## 9. Version History

| Version | Date | Author | Description |
|---------|------|--------|-------------|
| 1.0 | 2026-04-06 | GAIA-QAO Council | Initial locked specification — all definitions final |

---

*This document is the canonical reference for the GAI-A tree structure.  All downstream specifications, branches, and assemblies must conform to these rules.  Modifications require L0 council approval and a new version of this document.*
