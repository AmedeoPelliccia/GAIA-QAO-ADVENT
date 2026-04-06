"""
SICOCA Statevector Simulator
=============================
A lightweight statevector-based quantum circuit simulator that
applies unitary gate matrices via Kronecker product expansion.

This simulator is used both for standalone circuit evaluation and
as the execution back-end for SICOCA interlocking chains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .circuit import Circuit
from .gates import Gate
from .qubit import basis_state, measure, probabilities


@dataclass
class SimulationResult:
    """Container for the output of a single circuit simulation."""

    circuit_name: str
    n_qubits: int
    statevector: np.ndarray
    counts: dict[str, int] = field(default_factory=dict)

    @property
    def probabilities(self) -> np.ndarray:
        return probabilities(self.statevector)

    def __repr__(self) -> str:
        top = sorted(self.counts.items(), key=lambda kv: -kv[1])[:5]
        top_str = ", ".join(f"|{k}⟩:{v}" for k, v in top)
        return (
            f"SimulationResult(circuit='{self.circuit_name}', "
            f"n_qubits={self.n_qubits}, top_counts=[{top_str}])"
        )


class Simulator:
    """Statevector quantum circuit simulator.

    Parameters
    ----------
    shots : int
        Default number of measurement samples (default 1024).
    seed : int or None
        Random seed for measurement sampling reproducibility.
    """

    def __init__(self, shots: int = 1024, seed: int | None = None):
        self.shots = shots
        self.seed = seed

    # ------------------------------------------------------------------
    # Core simulation
    # ------------------------------------------------------------------

    def run(self, circuit: Circuit,
            initial_state: np.ndarray | None = None,
            shots: int | None = None) -> SimulationResult:
        """Simulate a circuit and return the result.

        Parameters
        ----------
        circuit : Circuit
            The circuit to simulate.
        initial_state : np.ndarray or None
            Optional initial statevector.  Defaults to |00…0⟩.
        shots : int or None
            Override the default number of measurement shots.

        Returns
        -------
        SimulationResult
        """
        n = circuit.n_qubits
        state = (
            initial_state.copy()
            if initial_state is not None
            else basis_state(n, 0)
        )

        for gate in circuit.operations:
            unitary = self._expand_gate(gate, n)
            state = unitary @ state

        n_shots = shots if shots is not None else self.shots
        counts = measure(state, shots=n_shots, seed=self.seed)

        return SimulationResult(
            circuit_name=circuit.name,
            n_qubits=n,
            statevector=state,
            counts=counts,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _expand_gate(gate: Gate, n_qubits: int) -> np.ndarray:
        """Expand a gate's unitary to the full 2^n × 2^n Hilbert space.

        For single-qubit gates the expansion is straightforward via
        Kronecker products with identity matrices.

        For CNOT (2-qubit) gates an explicit permutation-aware
        construction is used to handle arbitrary control/target indices.
        """
        if gate.n_qubits == 1:
            return Simulator._expand_single(gate, n_qubits)
        if gate.n_qubits == 2:
            return Simulator._expand_two_qubit(gate, n_qubits)
        raise NotImplementedError(
            f"Gate expansion for {gate.n_qubits}-qubit gates "
            f"is not yet supported"
        )

    @staticmethod
    def _expand_single(gate: Gate, n_qubits: int) -> np.ndarray:
        """Expand a 1-qubit gate via Kronecker products."""
        (target,) = gate.target_qubits
        eye = np.eye(2, dtype=complex)
        matrices = [gate.matrix if i == target else eye
                    for i in range(n_qubits)]
        result = matrices[0]
        for m in matrices[1:]:
            result = np.kron(result, m)
        return result

    @staticmethod
    def _expand_two_qubit(gate: Gate, n_qubits: int) -> np.ndarray:
        """Expand a 2-qubit gate (e.g. CNOT) to the full space.

        Handles non-adjacent and reversed control/target ordering by
        constructing the operator via projector decomposition:

            CNOT_{c,t} = |0⟩⟨0|_c ⊗ I_t  +  |1⟩⟨1|_c ⊗ X_t

        This generalises cleanly to arbitrary qubit positions.
        """
        control, target = gate.target_qubits
        dim = 1 << n_qubits

        # Projectors for the control qubit
        p0 = np.array([[1, 0], [0, 0]], dtype=complex)  # |0><0|
        p1 = np.array([[0, 0], [0, 1]], dtype=complex)  # |1><1|

        # Action on target qubit when control is |1⟩
        x_gate = np.array([[0, 1], [1, 0]], dtype=complex)
        eye2 = np.eye(2, dtype=complex)

        # Build full-space terms
        term0_parts = []
        term1_parts = []
        for i in range(n_qubits):
            if i == control:
                term0_parts.append(p0)
                term1_parts.append(p1)
            elif i == target:
                term0_parts.append(eye2)
                term1_parts.append(x_gate)
            else:
                term0_parts.append(eye2)
                term1_parts.append(eye2)

        def kron_list(mats):
            result = mats[0]
            for m in mats[1:]:
                result = np.kron(result, m)
            return result

        return kron_list(term0_parts) + kron_list(term1_parts)
