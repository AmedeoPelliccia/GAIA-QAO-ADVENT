"""
SICOCA Gate Definitions
=======================
System Interlocking Chains Operating in Circuits Algorithms

Defines unitary quantum gate matrices for H (Hadamard), CNOT,
and the three Pauli gates (X, Y, Z).  Each gate is represented
as a callable ``Gate`` object carrying its matrix, qubit arity,
and human-readable label.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

import numpy as np

# ---------------------------------------------------------------------------
# Gate dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Gate:
    """Immutable representation of a quantum gate."""

    name: str
    matrix: np.ndarray
    n_qubits: int
    target_qubits: tuple[int, ...] = field(default=())

    # Convenience for pretty-printing in circuit diagrams
    def __repr__(self) -> str:
        return f"Gate({self.name}, qubits={self.target_qubits})"

    def bind(self, *qubits: int) -> "Gate":
        """Return a copy of this gate bound to specific qubit indices."""
        if len(qubits) != self.n_qubits:
            raise ValueError(
                f"Gate '{self.name}' requires {self.n_qubits} qubit(s), "
                f"got {len(qubits)}"
            )
        seen: set[int] = set()
        for q in qubits:
            if q < 0:
                raise ValueError(f"Qubit index must be non-negative, got {q}")
            if q in seen:
                raise ValueError(f"Duplicate qubit index {q}")
            seen.add(q)
        return Gate(
            name=self.name,
            matrix=self.matrix,
            n_qubits=self.n_qubits,
            target_qubits=tuple(qubits),
        )


# ---------------------------------------------------------------------------
# Standard gate library
# ---------------------------------------------------------------------------

_SQRT2_INV = 1.0 / math.sqrt(2)

# Hadamard gate  (1-qubit)
H = Gate(
    name="H",
    matrix=np.array(
        [[_SQRT2_INV, _SQRT2_INV],
         [_SQRT2_INV, -_SQRT2_INV]],
        dtype=complex,
    ),
    n_qubits=1,
)

# Pauli-X gate  (bit-flip, NOT)
X = Gate(
    name="X",
    matrix=np.array(
        [[0, 1],
         [1, 0]],
        dtype=complex,
    ),
    n_qubits=1,
)

# Pauli-Y gate
Y = Gate(
    name="Y",
    matrix=np.array(
        [[0, -1j],
         [1j, 0]],
        dtype=complex,
    ),
    n_qubits=1,
)

# Pauli-Z gate  (phase-flip)
Z = Gate(
    name="Z",
    matrix=np.array(
        [[1, 0],
         [0, -1]],
        dtype=complex,
    ),
    n_qubits=1,
)

# Identity gate (useful internally)
I = Gate(
    name="I",
    matrix=np.eye(2, dtype=complex),
    n_qubits=1,
)

# CNOT gate (2-qubit, control ⊗ target)
CNOT = Gate(
    name="CNOT",
    matrix=np.array(
        [[1, 0, 0, 0],
         [0, 1, 0, 0],
         [0, 0, 0, 1],
         [0, 0, 1, 0]],
        dtype=complex,
    ),
    n_qubits=2,
)


# ---------------------------------------------------------------------------
# Gate catalogue for lookup by name
# ---------------------------------------------------------------------------

GATE_CATALOGUE: dict[str, Gate] = {
    "H": H,
    "X": X,
    "Y": Y,
    "Z": Z,
    "I": I,
    "CNOT": CNOT,
    "CX": CNOT,  # alias
}


def get_gate(name: str) -> Gate:
    """Retrieve a gate template from the catalogue by name."""
    key = name.upper()
    if key not in GATE_CATALOGUE:
        raise KeyError(
            f"Unknown gate '{name}'. "
            f"Available: {sorted(GATE_CATALOGUE.keys())}"
        )
    return GATE_CATALOGUE[key]
