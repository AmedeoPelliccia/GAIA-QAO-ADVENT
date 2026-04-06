# Programs Index

> Master ALICE–BOB traceability matrix for all GAIA-QAO-ADVENT programs.

---

## ⚛️ DOMINIO CUÁNTICO-DATOS

Programs in this domain focus on quantum-enhanced data processing pipelines, bridging satellite telemetry, astrophysics observations, and quantum machine learning.

### ALICE Matrix — Quantum Data Programs

| ALICE ID | Program | Branch | Layer | Status | BOB Trace |
|----------|---------|--------|-------|--------|-----------|
| ALICE-EVO-001 | AM.PEL v2.0 — QML Transient Classifier | AMPEL + GAIR-SPACE | L5 | Development | BOB-EVO-001 |
| ALICE-EVO-002 | AM.PEL v2.0 — VQE Materials Kernel | AMPEL | L5 | Development | BOB-EVO-002 |
| ALICE-EVO-003 | AM.PEL v2.0 — CCSDS Telemetry Ingestor | GAIR-SPACE | L5 | Design | BOB-EVO-003 |
| ALICE-EVO-004 | AM.PEL v2.0 — PQC Provenance Ledger | AMPEL + GAIR-SPACE | L5 | Design | BOB-EVO-004 |
| ALICE-EVO-005 | AM.PEL v2.0 — QKD Link Simulator | GAIR-SPACE | L5 | Research | BOB-EVO-005 |

### BOB Traceability — Verification & Validation

| BOB ID | Verification Method | Target Standard | Hub |
|--------|-------------------|-----------------|-----|
| BOB-EVO-001 | Cross-validation against classical CNN baseline | DO-178C DAL-C | Naples ⚛️ |
| BOB-EVO-002 | VQE energy convergence vs. exact diagonalization | ECSS-E-ST-40C | Naples ⚛️ |
| BOB-EVO-003 | Bit-error-rate + latency against CCSDS Blue Book | ECSS-E-ST-50C | Bologna 🛡️ |
| BOB-EVO-004 | NIST PQC KAT vectors + Kyber-1024 interop | NIST SP 800-53 | Naples ⚛️ |
| BOB-EVO-005 | BB84 key-rate simulation vs. analytical bound | ITU-T Y.3800 | Bologna 🛡️ |

---

## 🛩️ DOMINIO AEROESPACIAL

| ALICE ID | Program | Branch | Layer | Status |
|----------|---------|--------|-------|--------|
| ALICE-AMPEL360-001 | AMPEL360 Q100 BWB Aircraft | AMPEL | L5 | Development |

---

## 🚀 DOMINIO ESPACIAL

| ALICE ID | Program | Branch | Layer | Status |
|----------|---------|--------|-------|--------|
| ALICE-SPACE-001 | GAIA-SPACE-LAUNCHER | GAIR-SPACE | L5 | Design |
| ALICE-SPACE-002 | SPACET Q10 Constellation | GAIR-SPACE | L5 | Design |

---

## 🤖 DOMINIO ROBÓTICA

| ALICE ID | Program | Branch | Layer | Status |
|----------|---------|--------|-------|--------|
| ALICE-ROBO-001 | ARES-X Exploration Platform | Robotics A+ | L5 | Research |

---

*This index follows the [GAI-A Tree Specification](../GAIA-TREE-SPEC.md).  All programs are registered in the AGGIX registry with canonical URIs.*
