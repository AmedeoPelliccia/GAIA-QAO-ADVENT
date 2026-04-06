"""
SICOCA Circuit Builder
======================
Provides the ``Circuit`` class used to compose a sequence of quantum
gate operations.  A circuit is the fundamental building block for
SICOCA interlocking chains.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import List, Optional

from .gates import Gate, get_gate, H, X, Y, Z, CNOT


@dataclass
class Circuit:
    """A quantum circuit consisting of an ordered sequence of bound gates.

    Parameters
    ----------
    n_qubits : int
        Number of qubits in this circuit.
    name : str
        Optional human-readable label for the circuit.
    """

    n_qubits: int
    name: str = "circuit"
    _operations: List[Gate] = field(default_factory=list, repr=False)
    metadata: dict = field(default_factory=dict)

    # -- gate shorthand methods ------------------------------------------------

    def h(self, qubit: int) -> "Circuit":
        """Apply Hadamard gate to *qubit*."""
        return self.add_gate(H, qubit)

    def x(self, qubit: int) -> "Circuit":
        """Apply Pauli-X gate to *qubit*."""
        return self.add_gate(X, qubit)

    def y(self, qubit: int) -> "Circuit":
        """Apply Pauli-Y gate to *qubit*."""
        return self.add_gate(Y, qubit)

    def z(self, qubit: int) -> "Circuit":
        """Apply Pauli-Z gate to *qubit*."""
        return self.add_gate(Z, qubit)

    def cnot(self, control: int, target: int) -> "Circuit":
        """Apply CNOT (CX) gate with *control* → *target*."""
        return self.add_gate(CNOT, control, target)

    # -- generic add -----------------------------------------------------------

    def add_gate(self, gate: Gate, *qubits: int) -> "Circuit":
        """Append a gate operation to this circuit.

        Parameters
        ----------
        gate : Gate
            A gate template (e.g. ``H``, ``CNOT``).
        *qubits : int
            Qubit indices the gate acts on.

        Returns
        -------
        Circuit
            ``self``, for fluent chaining.
        """
        for q in qubits:
            if q < 0 or q >= self.n_qubits:
                raise IndexError(
                    f"Qubit index {q} out of range for "
                    f"{self.n_qubits}-qubit circuit '{self.name}'"
                )
        bound = gate.bind(*qubits)
        self._operations.append(bound)
        return self

    # -- introspection ---------------------------------------------------------

    @property
    def operations(self) -> List[Gate]:
        """Return an immutable snapshot of gate operations."""
        return list(self._operations)

    @property
    def depth(self) -> int:
        """Circuit depth (number of gate layers)."""
        return len(self._operations)

    def copy(self) -> "Circuit":
        """Return a deep copy of this circuit."""
        return deepcopy(self)

    # -- visualisation ---------------------------------------------------------

    def draw(self) -> str:
        """Return an ASCII representation of the circuit."""
        lines: list[list[str]] = [[] for _ in range(self.n_qubits)]
        for op in self._operations:
            involved = set(op.target_qubits)
            for q in range(self.n_qubits):
                if q in involved:
                    if op.n_qubits == 1:
                        lines[q].append(f"[{op.name}]")
                    elif op.n_qubits == 2:
                        if q == op.target_qubits[0]:
                            lines[q].append(" ● ")
                        else:
                            lines[q].append(f"[{op.name}]")
                else:
                    # Pad to match the widest gate label
                    lines[q].append(" ── ")
        output_lines: list[str] = []
        for q in range(self.n_qubits):
            wire = "──".join(lines[q]) if lines[q] else ""
            output_lines.append(f"q{q}: ──{wire}──")
        return "\n".join(output_lines)

    def __repr__(self) -> str:
        return (
            f"Circuit(name='{self.name}', n_qubits={self.n_qubits}, "
            f"depth={self.depth})"
        )


# ---------------------------------------------------------------------------
# Pre-built circuit templates
# ---------------------------------------------------------------------------

def bell_pair(q0: int = 0, q1: int = 1) -> Circuit:
    """Return a 2-qubit Bell-state preparation circuit (|Φ⁺⟩)."""
    circ = Circuit(n_qubits=max(q0, q1) + 1, name="bell_pair")
    circ.h(q0).cnot(q0, q1)
    return circ


def ghz_state(n_qubits: int) -> Circuit:
    """Return an *n*-qubit GHZ state preparation circuit."""
    if n_qubits < 2:
        raise ValueError("GHZ state requires at least 2 qubits")
    circ = Circuit(n_qubits=n_qubits, name="ghz_state")
    circ.h(0)
    for q in range(1, n_qubits):
        circ.cnot(0, q)
    return circ


def superdense_coding_encode(bit0: int, bit1: int,
                             qubit: int = 0) -> Circuit:
    """Encode two classical bits via superdense coding on *qubit*.

    Assumes *qubit* is already part of a Bell pair.
    """
    circ = Circuit(n_qubits=qubit + 1, name="superdense_encode")
    if bit1:
        circ.x(qubit)
    if bit0:
        circ.z(qubit)
    return circ
