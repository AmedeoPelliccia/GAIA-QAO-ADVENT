"""
SICOCA – System Interlocking Chains Operating in Circuits Algorithms
====================================================================

A lightweight, pure-Python framework for building and simulating
quantum circuits composed of Hadamard (H), CNOT, and Pauli (X, Y, Z)
gates, organised into dependency-aware **interlocking chains**.

Quick start
-----------
>>> from sicoca import Circuit, Simulator, Chain, ChainManager
>>> circ = Circuit(2, name="bell").h(0).cnot(0, 1)
>>> result = Simulator(seed=42).run(circ)
>>> print(result)

Modules
-------
- ``gates``      – Gate definitions and catalogue
- ``qubit``      – Statevector helpers and measurement
- ``circuit``    – Circuit builder and templates
- ``simulator``  – Statevector simulation engine
- ``chains``     – Interlocking chain orchestration
"""

__version__ = "1.0.0"

# Gates
from .gates import Gate, H, X, Y, Z, I, CNOT, get_gate, GATE_CATALOGUE

# Qubit helpers
from .qubit import KET_0, KET_1, basis_state, tensor_product, measure, probabilities

# Circuit
from .circuit import Circuit, bell_pair, ghz_state, superdense_coding_encode

# Simulator
from .simulator import Simulator, SimulationResult

# Chains
from .chains import (
    Chain,
    ChainManager,
    Link,
    LinkStatus,
    InterlockPredicate,
    always_proceed,
    majority_outcome,
    fidelity_threshold,
)

__all__ = [
    # gates
    "Gate", "H", "X", "Y", "Z", "I", "CNOT", "get_gate", "GATE_CATALOGUE",
    # qubit
    "KET_0", "KET_1", "basis_state", "tensor_product", "measure", "probabilities",
    # circuit
    "Circuit", "bell_pair", "ghz_state", "superdense_coding_encode",
    # simulator
    "Simulator", "SimulationResult",
    # chains
    "Chain", "ChainManager", "Link", "LinkStatus",
    "InterlockPredicate", "always_proceed", "majority_outcome",
    "fidelity_threshold",
]
