"""
Quantum Circuit Manager for AMPEL360 Operating System.

Provides core quantum circuit infrastructure including:
- Quantum and classical register management
- Quantum gate operations (H, X, Y, Z, CNOT, CZ)
- Measurement protocols with configurable shot counts
- Circuit compilation and optimization (gate cancellation, merging)
- Error handling via dedicated exception hierarchy

Uses statevector simulation with NumPy for quantum state evolution.
Compatible with Python 3.9+.
"""

import copy
import math
from typing import Dict, List, Optional, Sequence, Tuple, Union

import numpy as np


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------

class QuantumCircuitError(Exception):
    """Base exception for quantum circuit operations."""


class GateError(QuantumCircuitError):
    """Raised when a gate operation is invalid or fails."""


class MeasurementError(QuantumCircuitError):
    """Raised when a measurement operation is invalid or fails."""


class CompilationError(QuantumCircuitError):
    """Raised when circuit compilation or optimization fails."""


# ---------------------------------------------------------------------------
# Registers
# ---------------------------------------------------------------------------

class QuantumRegister:
    """A named register of qubits.

    Parameters
    ----------
    size : int
        Number of qubits (must be >= 1).
    name : str
        Human-readable label, defaults to ``'q'``.
    """

    def __init__(self, size: int, name: str = "q"):
        if not isinstance(size, int) or size < 1:
            raise QuantumCircuitError(
                f"QuantumRegister size must be a positive integer, got {size!r}"
            )
        self.size = size
        self.name = name

    def __repr__(self) -> str:
        return f"QuantumRegister({self.size}, {self.name!r})"


class ClassicalRegister:
    """A named register of classical bits.

    Parameters
    ----------
    size : int
        Number of bits (must be >= 1).
    name : str
        Human-readable label, defaults to ``'c'``.
    """

    def __init__(self, size: int, name: str = "c"):
        if not isinstance(size, int) or size < 1:
            raise QuantumCircuitError(
                f"ClassicalRegister size must be a positive integer, got {size!r}"
            )
        self.size = size
        self.name = name

    def __repr__(self) -> str:
        return f"ClassicalRegister({self.size}, {self.name!r})"


# ---------------------------------------------------------------------------
# Gate definitions (unitary matrices)
# ---------------------------------------------------------------------------

# Single-qubit gates
_H = np.array([[1, 1], [1, -1]], dtype=complex) / math.sqrt(2)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
_I = np.eye(2, dtype=complex)

# Two-qubit gates (4×4)
_CNOT = np.array(
    [[1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 1],
     [0, 0, 1, 0]],
    dtype=complex,
)

_CZ = np.array(
    [[1, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 1, 0],
     [0, 0, 0, -1]],
    dtype=complex,
)

# Mapping from gate name to matrix (single-qubit)
_SINGLE_QUBIT_GATES: Dict[str, np.ndarray] = {
    "h": _H,
    "x": _X,
    "y": _Y,
    "z": _Z,
    "id": _I,
}

# Mapping from gate name to matrix (two-qubit)
_TWO_QUBIT_GATES: Dict[str, np.ndarray] = {
    "cx": _CNOT,
    "cz": _CZ,
}

# Gate inverse relationships (for cancellation optimisation)
_SELF_INVERSE_GATES = {"h", "x", "y", "z", "cx", "cz", "id"}


# ---------------------------------------------------------------------------
# QuantumCircuit
# ---------------------------------------------------------------------------

class QuantumCircuit:
    """Core quantum circuit for the AMPEL360 OS.

    Manages qubit state evolution, gate application, measurement, and
    circuit optimisation using statevector simulation.

    Parameters
    ----------
    qreg : QuantumRegister
        The quantum register to use.
    creg : ClassicalRegister
        The classical register for measurement results.
    """

    def __init__(self, qreg: QuantumRegister, creg: ClassicalRegister):
        if not isinstance(qreg, QuantumRegister):
            raise QuantumCircuitError(
                "First argument must be a QuantumRegister"
            )
        if not isinstance(creg, ClassicalRegister):
            raise QuantumCircuitError(
                "Second argument must be a ClassicalRegister"
            )

        self.qreg = qreg
        self.creg = creg
        self.num_qubits: int = qreg.size
        self.num_clbits: int = creg.size

        # Internal operation list: list of (gate_name, qubits, params)
        self._operations: List[Tuple[str, Tuple[int, ...], dict]] = []

        # Statevector (initialised to |00…0⟩)
        self._statevector: np.ndarray = np.zeros(
            2 ** self.num_qubits, dtype=complex
        )
        self._statevector[0] = 1.0 + 0j

        # Whether the statevector is synchronised with operations
        self._state_dirty: bool = False

        # Measurement results (populated after measure + simulate)
        self._classical_bits: Optional[List[int]] = None

    # ------------------------------------------------------------------
    # Qubit index validation
    # ------------------------------------------------------------------

    def _validate_qubit(self, qubit: int) -> None:
        """Raise ``GateError`` if *qubit* is out of range."""
        if not isinstance(qubit, int) or not (0 <= qubit < self.num_qubits):
            raise GateError(
                f"Qubit index {qubit!r} out of range for "
                f"{self.num_qubits}-qubit circuit"
            )

    def _validate_clbit(self, clbit: int) -> None:
        """Raise ``MeasurementError`` if *clbit* is out of range."""
        if not isinstance(clbit, int) or not (0 <= clbit < self.num_clbits):
            raise MeasurementError(
                f"Classical bit index {clbit!r} out of range for "
                f"{self.num_clbits}-bit register"
            )

    # ------------------------------------------------------------------
    # Single-qubit gates
    # ------------------------------------------------------------------

    def h(self, qubit: int) -> "QuantumCircuit":
        """Apply Hadamard gate to *qubit*."""
        self._validate_qubit(qubit)
        self._operations.append(("h", (qubit,), {}))
        self._state_dirty = True
        return self

    def x(self, qubit: int) -> "QuantumCircuit":
        """Apply Pauli-X (NOT) gate to *qubit*."""
        self._validate_qubit(qubit)
        self._operations.append(("x", (qubit,), {}))
        self._state_dirty = True
        return self

    def y(self, qubit: int) -> "QuantumCircuit":
        """Apply Pauli-Y gate to *qubit*."""
        self._validate_qubit(qubit)
        self._operations.append(("y", (qubit,), {}))
        self._state_dirty = True
        return self

    def z(self, qubit: int) -> "QuantumCircuit":
        """Apply Pauli-Z gate to *qubit*."""
        self._validate_qubit(qubit)
        self._operations.append(("z", (qubit,), {}))
        self._state_dirty = True
        return self

    def id(self, qubit: int) -> "QuantumCircuit":
        """Apply identity gate to *qubit* (no-op, useful for padding)."""
        self._validate_qubit(qubit)
        self._operations.append(("id", (qubit,), {}))
        self._state_dirty = True
        return self

    # ------------------------------------------------------------------
    # Two-qubit gates
    # ------------------------------------------------------------------

    def cx(self, control: int, target: int) -> "QuantumCircuit":
        """Apply CNOT gate with *control* → *target*."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise GateError("CNOT control and target must differ")
        self._operations.append(("cx", (control, target), {}))
        self._state_dirty = True
        return self

    def cz(self, control: int, target: int) -> "QuantumCircuit":
        """Apply controlled-Z gate with *control* → *target*."""
        self._validate_qubit(control)
        self._validate_qubit(target)
        if control == target:
            raise GateError("CZ control and target must differ")
        self._operations.append(("cz", (control, target), {}))
        self._state_dirty = True
        return self

    # ------------------------------------------------------------------
    # Measurement
    # ------------------------------------------------------------------

    def measure(
        self,
        qubits: Union[int, Sequence[int], QuantumRegister],
        clbits: Union[int, Sequence[int], ClassicalRegister],
    ) -> "QuantumCircuit":
        """Add measurement operations mapping *qubits* → *clbits*.

        Parameters
        ----------
        qubits : int, sequence of int, or QuantumRegister
            Qubit(s) to measure.
        clbits : int, sequence of int, or ClassicalRegister
            Classical bit(s) to store results.
        """
        if isinstance(qubits, QuantumRegister):
            qubit_list = list(range(qubits.size))
        elif isinstance(qubits, int):
            qubit_list = [qubits]
        else:
            qubit_list = list(qubits)

        if isinstance(clbits, ClassicalRegister):
            clbit_list = list(range(clbits.size))
        elif isinstance(clbits, int):
            clbit_list = [clbits]
        else:
            clbit_list = list(clbits)

        if len(qubit_list) != len(clbit_list):
            raise MeasurementError(
                f"Number of qubits ({len(qubit_list)}) and classical bits "
                f"({len(clbit_list)}) must match for measurement"
            )

        for q in qubit_list:
            self._validate_qubit(q)
        for c in clbit_list:
            self._validate_clbit(c)

        for q, c in zip(qubit_list, clbit_list):
            self._operations.append(("measure", (q,), {"clbit": c}))

        return self

    # ------------------------------------------------------------------
    # Statevector simulation helpers
    # ------------------------------------------------------------------

    def _apply_single_gate(
        self, gate_matrix: np.ndarray, qubit: int
    ) -> None:
        """Apply a single-qubit *gate_matrix* to the statevector."""
        n = self.num_qubits
        # Build full operator via tensor product
        ops = [_I] * n
        ops[qubit] = gate_matrix
        full = ops[0]
        for op in ops[1:]:
            full = np.kron(full, op)
        self._statevector = full @ self._statevector

    def _apply_two_qubit_gate(
        self, gate_name: str, control: int, target: int
    ) -> None:
        """Apply a two-qubit gate to the statevector."""
        n = self.num_qubits
        dim = 2 ** n
        gate_matrix = _TWO_QUBIT_GATES[gate_name]
        result = np.zeros(dim, dtype=complex)

        for i in range(dim):
            bits = [(i >> (n - 1 - k)) & 1 for k in range(n)]
            c_bit = bits[control]
            t_bit = bits[target]
            # Index into the 2-qubit sub-space
            sub_idx = (c_bit << 1) | t_bit
            for j in range(4):
                if gate_matrix[j, sub_idx] == 0:
                    continue
                new_c = (j >> 1) & 1
                new_t = j & 1
                new_bits = bits.copy()
                new_bits[control] = new_c
                new_bits[target] = new_t
                new_i = 0
                for k, b in enumerate(new_bits):
                    new_i |= b << (n - 1 - k)
                result[new_i] += gate_matrix[j, sub_idx] * self._statevector[i]

        self._statevector = result

    def _sync_statevector(self) -> None:
        """Replay all non-measure operations to rebuild the statevector."""
        self._statevector = np.zeros(2 ** self.num_qubits, dtype=complex)
        self._statevector[0] = 1.0 + 0j

        for gate_name, qubits, _params in self._operations:
            if gate_name == "measure":
                continue
            if gate_name in _SINGLE_QUBIT_GATES:
                self._apply_single_gate(
                    _SINGLE_QUBIT_GATES[gate_name], qubits[0]
                )
            elif gate_name in _TWO_QUBIT_GATES:
                self._apply_two_qubit_gate(gate_name, qubits[0], qubits[1])

        self._state_dirty = False

    # ------------------------------------------------------------------
    # Execution / Simulation
    # ------------------------------------------------------------------

    def simulate(self, shots: int = 1024) -> Dict[str, int]:
        """Simulate the circuit and return measurement counts.

        Parameters
        ----------
        shots : int
            Number of measurement repetitions (default 1024).

        Returns
        -------
        dict
            Mapping of bitstring → count, e.g. ``{"0000": 512, "1111": 512}``.

        Raises
        ------
        MeasurementError
            If the circuit contains no measurement operations.
        CompilationError
            If the circuit cannot be executed.
        """
        if shots < 1:
            raise MeasurementError("shots must be >= 1")

        measure_ops = [
            op for op in self._operations if op[0] == "measure"
        ]
        if not measure_ops:
            raise MeasurementError(
                "Circuit has no measurement operations; "
                "add measurements before simulating"
            )

        # Ensure statevector is up to date
        if self._state_dirty:
            self._sync_statevector()

        probabilities = np.abs(self._statevector) ** 2

        # Normalise to guard against floating-point drift
        prob_sum = probabilities.sum()
        if prob_sum < 1e-10:
            raise CompilationError(
                "Statevector has near-zero norm; circuit may be invalid"
            )
        probabilities = probabilities / prob_sum

        # Sample outcomes
        dim = 2 ** self.num_qubits
        indices = np.arange(dim)

        rng = np.random.default_rng()
        sampled = rng.choice(indices, size=shots, p=probabilities)

        # Build measured-qubit → classical-bit mapping
        measured_qubits: List[int] = []
        clbit_targets: List[int] = []
        for _gate, qubits, params in measure_ops:
            measured_qubits.append(qubits[0])
            clbit_targets.append(params["clbit"])

        counts: Dict[str, int] = {}
        for idx in sampled:
            bits = [(idx >> (self.num_qubits - 1 - k)) & 1
                    for k in range(self.num_qubits)]
            result_bits = [0] * self.num_clbits
            for q, c in zip(measured_qubits, clbit_targets):
                result_bits[c] = bits[q]
            bitstring = "".join(str(b) for b in result_bits)
            counts[bitstring] = counts.get(bitstring, 0) + 1

        return counts

    # ------------------------------------------------------------------
    # Circuit compilation and optimisation
    # ------------------------------------------------------------------

    def compile(self) -> "QuantumCircuit":
        """Compile the circuit by applying optimisation passes.

        Currently implements:
        1. **Identity removal** – drops ``id`` gates.
        2. **Adjacent inverse cancellation** – removes consecutive
           self-inverse gates on the same qubit(s).
        3. **Hadamard-X-Hadamard → Z** fusion.

        Returns
        -------
        QuantumCircuit
            A new, optimised circuit.
        """
        optimised_ops = list(self._operations)

        # Pass 1: Remove identity gates
        optimised_ops = [
            op for op in optimised_ops if op[0] != "id"
        ]

        # Pass 2: Cancel adjacent self-inverse gates
        changed = True
        while changed:
            changed = False
            new_ops: List[Tuple[str, Tuple[int, ...], dict]] = []
            i = 0
            while i < len(optimised_ops):
                if (
                    i + 1 < len(optimised_ops)
                    and optimised_ops[i][0] == optimised_ops[i + 1][0]
                    and optimised_ops[i][1] == optimised_ops[i + 1][1]
                    and optimised_ops[i][0] in _SELF_INVERSE_GATES
                    and optimised_ops[i][0] != "measure"
                ):
                    # Two identical self-inverse gates cancel out
                    i += 2
                    changed = True
                else:
                    new_ops.append(optimised_ops[i])
                    i += 1
            optimised_ops = new_ops

        # Pass 3: H-X-H → Z fusion
        new_ops = []
        i = 0
        while i < len(optimised_ops):
            if (
                i + 2 < len(optimised_ops)
                and optimised_ops[i][0] == "h"
                and optimised_ops[i + 1][0] == "x"
                and optimised_ops[i + 2][0] == "h"
                and optimised_ops[i][1] == optimised_ops[i + 1][1]
                and optimised_ops[i][1] == optimised_ops[i + 2][1]
            ):
                new_ops.append(("z", optimised_ops[i][1], {}))
                i += 3
            else:
                new_ops.append(optimised_ops[i])
                i += 1
        optimised_ops = new_ops

        # Build the new circuit
        new_circuit = QuantumCircuit(
            QuantumRegister(self.num_qubits, self.qreg.name),
            ClassicalRegister(self.num_clbits, self.creg.name),
        )
        new_circuit._operations = optimised_ops
        new_circuit._state_dirty = True
        return new_circuit

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def depth(self) -> int:
        """Return the circuit depth (non-measure operations only)."""
        return sum(1 for op in self._operations if op[0] != "measure")

    @property
    def gate_count(self) -> Dict[str, int]:
        """Return a gate-type → count mapping."""
        counts: Dict[str, int] = {}
        for gate_name, _q, _p in self._operations:
            counts[gate_name] = counts.get(gate_name, 0) + 1
        return counts

    @property
    def operations(self) -> List[Tuple[str, Tuple[int, ...], dict]]:
        """Return a copy of the operation list."""
        return list(self._operations)

    def get_statevector(self) -> np.ndarray:
        """Return the current statevector (synchronising if needed)."""
        if self._state_dirty:
            self._sync_statevector()
        return self._statevector.copy()

    def copy(self) -> "QuantumCircuit":
        """Return a deep copy of this circuit."""
        return copy.deepcopy(self)

    def reset(self) -> "QuantumCircuit":
        """Clear all operations and reset to |00…0⟩."""
        self._operations.clear()
        self._statevector = np.zeros(2 ** self.num_qubits, dtype=complex)
        self._statevector[0] = 1.0 + 0j
        self._state_dirty = False
        self._classical_bits = None
        return self

    def __repr__(self) -> str:
        return (
            f"QuantumCircuit(qubits={self.num_qubits}, "
            f"clbits={self.num_clbits}, "
            f"depth={self.depth})"
        )
