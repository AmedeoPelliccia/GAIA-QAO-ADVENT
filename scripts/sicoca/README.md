---
title: "SICOCA — System Interlocking Chains Operating in Circuits Algorithms"
description: "Pure-Python quantum circuit framework with H, CNOT, Pauli gates and interlocking chains"
version: "1.0.0"
python_requires: ">=3.9"
dependencies: [numpy]
layer: L2
aggix_uri: "aggix://gaia/aggix/core/ASM/sicoca@1.0.0"
author: GAIA-QAO
tags: [SICOCA, quantum, circuits, simulation, chains]
---

# SICOCA – System Interlocking Chains Operating in Circuits Algorithms

> **Version 1.0.0** · Part of the [GAIA-QAO-ADVENT](../../README.md) quantum-aerospace framework

## Overview

SICOCA is a lightweight, pure-Python quantum circuit framework that
implements **interlocking chains** — directed sequences of quantum circuits
whose execution is governed by dependency predicates evaluated at runtime.

### Supported gates

| Gate | Symbol | Qubits | Description |
|------|--------|--------|-------------|
| Hadamard | `H` | 1 | Creates equal superposition: `\|0⟩ → (\|0⟩ + \|1⟩)/√2` |
| Pauli-X | `X` | 1 | Bit-flip (quantum NOT): `\|0⟩ ↔ \|1⟩` |
| Pauli-Y | `Y` | 1 | Bit + phase flip |
| Pauli-Z | `Z` | 1 | Phase-flip: `\|1⟩ → −\|1⟩` |
| CNOT | `CNOT` | 2 | Controlled-NOT: flips target when control is `\|1⟩` |
| Identity | `I` | 1 | No-op (used internally) |

### Core concepts

```
Chain ──▶ Link 0 ──▶ Link 1 ──▶ Link 2
           │           │           │
         Circuit    Circuit    Circuit
                   ▲           ▲
              interlock    interlock
           (checks prev   (checks prev
            result)         result)
```

- **Gate** – immutable unitary matrix with qubit arity metadata.
- **Circuit** – ordered sequence of bound gate operations on `n` qubits.
- **Simulator** – statevector engine that applies the circuit's unitary
  evolution and samples measurement outcomes.
- **Link** – a circuit + an interlock predicate.
- **Chain** – ordered list of links executed head-to-tail; execution halts
  if any interlock fails.
- **ChainManager** – orchestrator that registers, executes, and reports
  on multiple chains.

## Quick start

```python
from sicoca import Circuit, Simulator, Chain, ChainManager, bell_pair, majority_outcome

# 1. Build a circuit
circ = Circuit(2, name="bell_state")
circ.h(0).cnot(0, 1)          # Fluent API

# 2. Simulate
sim = Simulator(shots=1024, seed=42)
result = sim.run(circ)
print(result.counts)           # {'00': ~512, '11': ~512}

# 3. Interlocking chain
chain = Chain(name="entanglement_pipeline")
chain.add_link(bell_pair(), label="Prepare Bell pair")
chain.add_link(
    Circuit(2).x(0),
    interlock=majority_outcome("00"),
    label="Conditional X flip",
)

mgr = ChainManager(simulator=sim)
mgr.register_chain(chain)
mgr.execute_chain("entanglement_pipeline")
print(mgr.summary())
```

## CLI usage

```bash
# Run all demos
python -m sicoca.cli demo

# Individual demos
python -m sicoca.cli bell
python -m sicoca.cli ghz 5
python -m sicoca.cli pauli
python -m sicoca.cli chain
```

## Package structure

```
scripts/sicoca/
├── __init__.py       # Public API re-exports
├── __main__.py       # python -m sicoca entry point
├── gates.py          # H, X, Y, Z, I, CNOT gate definitions
├── qubit.py          # Statevector and measurement helpers
├── circuit.py        # Circuit builder + templates
├── simulator.py      # Statevector simulation engine
├── chains.py         # Interlocking chain orchestration
├── cli.py            # Command-line demonstrations
├── README.md         # This file
└── tests/
    └── test_sicoca.py  # Comprehensive test suite
```

## Running tests

```bash
cd scripts
python -m pytest sicoca/tests/test_sicoca.py -v
# or
python sicoca/tests/test_sicoca.py
```

## Architecture

### Gate expansion

Single-qubit gates are expanded to the full `2^n × 2^n` Hilbert space via
Kronecker products with identity matrices.

Two-qubit gates (CNOT) use a **projector decomposition**:

```
CNOT_{c,t} = |0⟩⟨0|_c ⊗ I_t  +  |1⟩⟨1|_c ⊗ X_t
```

This handles arbitrary (non-adjacent, reversed) control/target positions
without permutation matrices.

### Interlock predicates

Built-in predicates:

| Predicate | Description |
|-----------|-------------|
| `always_proceed` | Always allows the next link (default) |
| `majority_outcome(bitstring)` | Passes when the target bitstring is the most frequent measurement outcome |
| `fidelity_threshold(min, ref)` | Passes when state fidelity with a reference state exceeds a threshold |

Custom predicates can be any callable with signature
`(SimulationResult) -> bool`.

## Dependencies

- **Python ≥ 3.9**
- **NumPy** (only external dependency)

No external quantum computing frameworks (Qiskit, Cirq, etc.) are required.
