# AM.PEL v2.0 — AMPEL-EVO Program Index

> Quantum-Enhanced Aerospace Astrophysics Data Pipeline

**Document ID:** AMPEL-EVO-2026-04-05-PAPALAIKED-V2  
**Evolved from:** PapaLaiked AM.PEL baseline (v1.x)  
**AGGIX URI:** `aggix://gaia/ampel/ampel-evo/PRG/papalaiked-v2@2.0.0`  
**GAI-A Tree:** L5 (Program) → L3a AMPEL + L3c GAIR-SPACE  

---

## ALICE–BOB Traceability

| ALICE ID | Component | BOB ID | V&V Method | Standard |
|----------|-----------|--------|------------|----------|
| ALICE-EVO-001 | QML Transient Classifier | BOB-EVO-001 | Cross-validation vs. CNN | DO-178C DAL-C |
| ALICE-EVO-002 | VQE Materials Kernel | BOB-EVO-002 | Energy convergence test | ECSS-E-ST-40C |
| ALICE-EVO-003 | CCSDS Telemetry Ingestor | BOB-EVO-003 | BER + latency test | ECSS-E-ST-50C |
| ALICE-EVO-004 | PQC Provenance Ledger | BOB-EVO-004 | NIST PQC KAT vectors | NIST SP 800-53 |
| ALICE-EVO-005 | QKD Link Simulator | BOB-EVO-005 | BB84 key-rate simulation | ITU-T Y.3800 |

---

## Hub Alignment

| Hub | Role | Data Streams |
|-----|------|-------------|
| **Naples** ⚛️ Quantum Technology Hub | QML training, propulsion sensors | Nanotech telemetry, neutrino data, quantum propulsion metrics |
| **Bologna** 🛡️ Earth Protection Center | SSA pipelines, observation data | Satellite imagery, catastrophe alerts, deep-space radar |

---

## Specifications

- [AMPEL-EVO-2026-04-05-PAPALAIKED-V2.md](./AMPEL-EVO-2026-04-05-PAPALAIKED-V2.md) — Full 8-section production specification

---

## Roadmap

| Milestone | Target | Status |
|-----------|--------|--------|
| Aerospace testbed deployment | Q3 2026 | Planned |
| Open-source release (Apache 2.0) | Q4 2026 | Planned |
| ESA Quantum Mission integration | 2027 | Planned |

---

*Parent index: [programs/readme.md](../readme.md) · Tree spec: [GAIA-TREE-SPEC.md](../../GAIA-TREE-SPEC.md)*
