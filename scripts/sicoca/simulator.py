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

    def __init__(self, shots: int = 1024, seed: Optional[int] = None):
        self.shots = shots
        self.seed = seed

    # ------------------------------------------------------------------
    # Core simulation
    # ------------------------------------------------------------------

    def run(self, circuit: Circuit,
            initial_state: Optional[np.ndarray] = None,
            shots: Optional[int] = None) -> SimulationResult:
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
        if initial_state is not None:
            dim = 1 << n
            if initial_state.shape != (dim,):
                raise ValueError(
                    f"initial_state length {initial_state.shape} does not "
                    f"match expected dimension ({dim},) for {n} qubits"
                )
            state = initial_state.copy()
        else:
            state = basis_state(n, 0)

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
    # Convenience launch
    # ------------------------------------------------------------------

    @classmethod
    def launch(cls, circuit: Circuit, shots: int = 1024,
               seed: Optional[int] = None) -> SimulationResult:
        """One-shot convenience: create a simulator, run a circuit, return
        the result.

        Parameters
        ----------
        circuit : Circuit
            The circuit to simulate.
        shots : int
            Number of measurement samples.
        seed : int or None
            Random seed for reproducibility.

        Returns
        -------
        SimulationResult
        """
        return cls(shots=shots, seed=seed).run(circuit)

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
        """Expand a generic 2-qubit gate to the full space.

        The 4×4 ``gate.matrix`` is interpreted in the qubit order given by
        ``gate.target_qubits``. This supports arbitrary 2-qubit unitaries,
        including non-adjacent qubits and reversed qubit ordering.
        """
        q0, q1 = gate.target_qubits
        gate_matrix = np.asarray(gate.matrix, dtype=complex)
        if gate_matrix.shape != (4, 4):
            raise ValueError(
                f"2-qubit gate matrix must have shape (4, 4), "
                f"got {gate_matrix.shape}"
            )

        dim = 1 << n_qubits
        full_matrix = np.zeros((dim, dim), dtype=complex)

        for input_index in range(dim):
            input_bits = [(input_index >> (n_qubits - 1 - i)) & 1
                          for i in range(n_qubits)]
            two_qubit_input = (input_bits[q0] << 1) | input_bits[q1]

            for two_qubit_output in range(4):
                amplitude = gate_matrix[two_qubit_output, two_qubit_input]
                if amplitude == 0:
                    continue

                output_bits = input_bits.copy()
                output_bits[q0] = (two_qubit_output >> 1) & 1
                output_bits[q1] = two_qubit_output & 1
                output_index = 0
                for bit in output_bits:
                    output_index = (output_index << 1) | bit
                full_matrix[output_index, input_index] += amplitude

        return full_matrix
