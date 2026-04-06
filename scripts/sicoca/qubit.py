"""
SICOCA Qubit State Representation
==================================
Provides helpers for constructing and inspecting multi-qubit
statevectors used by the SICOCA simulator.
"""

from __future__ import annotations

from functools import reduce
from typing import Sequence

import numpy as np

# ---------------------------------------------------------------------------
# Basis states
# ---------------------------------------------------------------------------

KET_0 = np.array([1, 0], dtype=complex)
KET_1 = np.array([0, 1], dtype=complex)


def basis_state(n_qubits: int, index: int = 0) -> np.ndarray:
    """Return computational basis state |index⟩ for *n_qubits* qubits.

    Parameters
    ----------
    n_qubits : int
        Total number of qubits.
    index : int
        Decimal representation of the desired basis state
        (0 … 2**n_qubits - 1).

    Returns
    -------
    np.ndarray
        Column-vector of length 2**n_qubits.
    """
    dim = 1 << n_qubits
    if not 0 <= index < dim:
        raise ValueError(
            f"Basis index {index} out of range for {n_qubits}-qubit system "
            f"(valid 0..{dim - 1})"
        )
    state = np.zeros(dim, dtype=complex)
    state[index] = 1.0
    return state


def tensor_product(states: Sequence[np.ndarray]) -> np.ndarray:
    """Compute the Kronecker (tensor) product of a sequence of vectors."""
    return reduce(np.kron, states)


# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------

def probabilities(statevector: np.ndarray) -> np.ndarray:
    """Return the measurement probability distribution |α_i|²."""
    return np.abs(statevector) ** 2


def measure(statevector: np.ndarray, shots: int = 1024,
            seed: int | None = None) -> dict[str, int]:
    """Sample measurement outcomes from a statevector.

    Parameters
    ----------
    statevector : np.ndarray
        Normalized statevector.
    shots : int
        Number of measurement samples.
    seed : int or None
        Random seed for reproducibility.

    Returns
    -------
    dict[str, int]
        Mapping from bitstring label (e.g. ``"00"``, ``"11"``) to count.
    """
    rng = np.random.default_rng(seed)
    n_qubits = int(np.log2(len(statevector)))
    probs = probabilities(statevector)
    indices = rng.choice(len(probs), size=shots, p=probs)
    counts: dict[str, int] = {}
    for idx in indices:
        label = format(idx, f"0{n_qubits}b")
        counts[label] = counts.get(label, 0) + 1
    return counts
