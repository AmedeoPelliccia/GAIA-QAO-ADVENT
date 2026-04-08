"""Unit tests for src.quantum.circuit_manager."""

import math

import numpy as np
import pytest

from src.quantum.circuit_manager import (
    ClassicalRegister,
    GateError,
    MeasurementError,
    QuantumCircuit,
    QuantumCircuitError,
    QuantumRegister,
)


# ---------------------------------------------------------------
# Register tests
# ---------------------------------------------------------------

class TestQuantumRegister:
    def test_creation(self):
        qr = QuantumRegister(4, "q")
        assert qr.size == 4
        assert qr.name == "q"

    def test_default_name(self):
        qr = QuantumRegister(2)
        assert qr.name == "q"

    def test_invalid_size_zero(self):
        with pytest.raises(QuantumCircuitError):
            QuantumRegister(0)

    def test_invalid_size_negative(self):
        with pytest.raises(QuantumCircuitError):
            QuantumRegister(-1)

    def test_invalid_size_type(self):
        with pytest.raises(QuantumCircuitError):
            QuantumRegister(2.5)  # type: ignore[arg-type]

    def test_repr(self):
        assert repr(QuantumRegister(3, "x")) == "QuantumRegister(3, 'x')"


class TestClassicalRegister:
    def test_creation(self):
        cr = ClassicalRegister(4, "c")
        assert cr.size == 4
        assert cr.name == "c"

    def test_invalid_size(self):
        with pytest.raises(QuantumCircuitError):
            ClassicalRegister(0)

    def test_repr(self):
        assert repr(ClassicalRegister(2, "m")) == "ClassicalRegister(2, 'm')"


# ---------------------------------------------------------------
# Circuit creation tests
# ---------------------------------------------------------------

class TestQuantumCircuitCreation:
    def test_basic_creation(self):
        qr = QuantumRegister(4, "q")
        cr = ClassicalRegister(4, "c")
        qc = QuantumCircuit(qr, cr)
        assert qc.num_qubits == 4
        assert qc.num_clbits == 4
        assert qc.depth == 0

    def test_invalid_qreg_type(self):
        with pytest.raises(QuantumCircuitError):
            QuantumCircuit("bad", ClassicalRegister(1))  # type: ignore[arg-type]

    def test_invalid_creg_type(self):
        with pytest.raises(QuantumCircuitError):
            QuantumCircuit(QuantumRegister(1), "bad")  # type: ignore[arg-type]

    def test_initial_statevector(self):
        qr = QuantumRegister(2, "q")
        cr = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qr, cr)
        sv = qc.get_statevector()
        assert sv[0] == 1.0 + 0j
        assert np.allclose(sv[1:], 0)

    def test_repr(self):
        qr = QuantumRegister(2, "q")
        cr = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qr, cr)
        assert "qubits=2" in repr(qc)


# ---------------------------------------------------------------
# Single-qubit gate tests
# ---------------------------------------------------------------

class TestSingleQubitGates:
    def _make_circuit(self, n: int = 2):
        return QuantumCircuit(QuantumRegister(n), ClassicalRegister(n))

    def test_hadamard_creates_superposition(self):
        qc = self._make_circuit(1)
        qc.h(0)
        sv = qc.get_statevector()
        expected = np.array([1, 1], dtype=complex) / math.sqrt(2)
        assert np.allclose(sv, expected)

    def test_pauli_x_flips(self):
        qc = self._make_circuit(1)
        qc.x(0)
        sv = qc.get_statevector()
        assert np.isclose(sv[1], 1.0)
        assert np.isclose(sv[0], 0.0)

    def test_pauli_y(self):
        qc = self._make_circuit(1)
        qc.y(0)
        sv = qc.get_statevector()
        # Y|0⟩ = i|1⟩
        assert np.isclose(sv[0], 0.0)
        assert np.isclose(sv[1], 1j)

    def test_pauli_z_on_zero(self):
        qc = self._make_circuit(1)
        qc.z(0)
        sv = qc.get_statevector()
        # Z|0⟩ = |0⟩
        assert np.isclose(sv[0], 1.0)

    def test_pauli_z_on_one(self):
        qc = self._make_circuit(1)
        qc.x(0)  # prepare |1⟩
        qc.z(0)
        sv = qc.get_statevector()
        # Z|1⟩ = -|1⟩
        assert np.isclose(sv[1], -1.0)

    def test_identity(self):
        qc = self._make_circuit(1)
        qc.id(0)
        sv = qc.get_statevector()
        assert np.isclose(sv[0], 1.0)

    def test_double_x_returns_to_zero(self):
        qc = self._make_circuit(1)
        qc.x(0)
        qc.x(0)
        sv = qc.get_statevector()
        assert np.isclose(sv[0], 1.0)

    def test_invalid_qubit_index(self):
        qc = self._make_circuit(2)
        with pytest.raises(GateError):
            qc.h(5)

    def test_negative_qubit_index(self):
        qc = self._make_circuit(2)
        with pytest.raises(GateError):
            qc.x(-1)

    def test_gate_returns_circuit(self):
        """Gates return self for chaining."""
        qc = self._make_circuit(2)
        result = qc.h(0)
        assert result is qc


# ---------------------------------------------------------------
# Two-qubit gate tests
# ---------------------------------------------------------------

class TestTwoQubitGates:
    def _make_circuit(self, n: int = 2):
        return QuantumCircuit(QuantumRegister(n), ClassicalRegister(n))

    def test_cnot_no_flip_when_control_zero(self):
        qc = self._make_circuit(2)
        qc.cx(0, 1)
        sv = qc.get_statevector()
        # |00⟩ → |00⟩
        assert np.isclose(sv[0], 1.0)

    def test_cnot_flips_when_control_one(self):
        qc = self._make_circuit(2)
        qc.x(0)   # |10⟩
        qc.cx(0, 1)
        sv = qc.get_statevector()
        # |10⟩ → |11⟩ which is index 3
        assert np.isclose(sv[3], 1.0)

    def test_bell_state(self):
        """H on q0, CNOT(q0,q1) creates Bell state (|00⟩+|11⟩)/√2."""
        qc = self._make_circuit(2)
        qc.h(0)
        qc.cx(0, 1)
        sv = qc.get_statevector()
        expected = np.zeros(4, dtype=complex)
        expected[0] = 1 / math.sqrt(2)
        expected[3] = 1 / math.sqrt(2)
        assert np.allclose(sv, expected)

    def test_cz_gate(self):
        qc = self._make_circuit(2)
        qc.x(0)
        qc.x(1)  # |11⟩
        qc.cz(0, 1)
        sv = qc.get_statevector()
        # CZ|11⟩ = -|11⟩
        assert np.isclose(sv[3], -1.0)

    def test_cnot_same_qubit_raises(self):
        qc = self._make_circuit(2)
        with pytest.raises(GateError):
            qc.cx(0, 0)

    def test_cz_same_qubit_raises(self):
        qc = self._make_circuit(2)
        with pytest.raises(GateError):
            qc.cz(1, 1)

    def test_cnot_invalid_qubit(self):
        qc = self._make_circuit(2)
        with pytest.raises(GateError):
            qc.cx(0, 5)


# ---------------------------------------------------------------
# Measurement tests
# ---------------------------------------------------------------

class TestMeasurement:
    def _make_circuit(self, n: int = 2):
        return QuantumCircuit(QuantumRegister(n), ClassicalRegister(n))

    def test_measure_all(self):
        qr = QuantumRegister(2, "q")
        cr = ClassicalRegister(2, "c")
        qc = QuantumCircuit(qr, cr)
        qc.measure(qr, cr)
        counts = qc.simulate(shots=100)
        assert "00" in counts
        assert sum(counts.values()) == 100

    def test_measure_single_qubit(self):
        qc = self._make_circuit(2)
        qc.measure(0, 0)
        counts = qc.simulate(shots=50)
        assert sum(counts.values()) == 50

    def test_measure_x_gate_always_one(self):
        qc = self._make_circuit(1)
        qc.x(0)
        qc.measure(0, 0)
        counts = qc.simulate(shots=100)
        assert counts == {"1": 100}

    def test_measure_mismatch_raises(self):
        qc = self._make_circuit(2)
        with pytest.raises(MeasurementError):
            qc.measure([0, 1], [0])

    def test_no_measurement_raises(self):
        qc = self._make_circuit(1)
        qc.h(0)
        with pytest.raises(MeasurementError):
            qc.simulate()

    def test_invalid_clbit_raises(self):
        qc = self._make_circuit(2)
        with pytest.raises(MeasurementError):
            qc.measure(0, 5)

    def test_bell_state_measurement(self):
        """Bell state should produce only 00 or 11."""
        qc = self._make_circuit(2)
        qc.h(0)
        qc.cx(0, 1)
        qr = qc.qreg
        cr = qc.creg
        qc.measure(qr, cr)
        counts = qc.simulate(shots=1000)
        for bitstring in counts:
            assert bitstring in ("00", "11")
        assert sum(counts.values()) == 1000

    def test_shots_must_be_positive(self):
        qc = self._make_circuit(1)
        qc.measure(0, 0)
        with pytest.raises(MeasurementError):
            qc.simulate(shots=0)

    def test_superposition_distribution(self):
        """H|0⟩ measured should give roughly 50/50."""
        qc = self._make_circuit(1)
        qc.h(0)
        qc.measure(0, 0)
        counts = qc.simulate(shots=10000)
        # Both outcomes should appear; allow wide tolerance
        assert "0" in counts and "1" in counts
        ratio = counts["0"] / 10000
        assert 0.4 < ratio < 0.6


# ---------------------------------------------------------------
# Compilation / optimisation tests
# ---------------------------------------------------------------

class TestCompilation:
    def _make_circuit(self, n: int = 2):
        return QuantumCircuit(QuantumRegister(n), ClassicalRegister(n))

    def test_identity_removal(self):
        qc = self._make_circuit(1)
        qc.id(0)
        qc.id(0)
        qc.h(0)
        compiled = qc.compile()
        assert compiled.depth == 1
        assert compiled.gate_count == {"h": 1}

    def test_double_x_cancellation(self):
        qc = self._make_circuit(1)
        qc.x(0)
        qc.x(0)
        compiled = qc.compile()
        assert compiled.depth == 0

    def test_double_h_cancellation(self):
        qc = self._make_circuit(1)
        qc.h(0)
        qc.h(0)
        compiled = qc.compile()
        assert compiled.depth == 0

    def test_hxh_to_z_fusion(self):
        qc = self._make_circuit(1)
        qc.h(0)
        qc.x(0)
        qc.h(0)
        compiled = qc.compile()
        assert compiled.gate_count == {"z": 1}

    def test_compile_preserves_measurements(self):
        qc = self._make_circuit(1)
        qc.id(0)
        qc.h(0)
        qc.measure(0, 0)
        compiled = qc.compile()
        assert "measure" in compiled.gate_count

    def test_compiled_circuit_runs(self):
        """Compiled circuit should simulate correctly."""
        qc = self._make_circuit(2)
        qc.h(0)
        qc.id(0)
        qc.cx(0, 1)
        qc.measure(qc.qreg, qc.creg)
        compiled = qc.compile()
        counts = compiled.simulate(shots=500)
        for bs in counts:
            assert bs in ("00", "11")

    def test_compile_returns_new_circuit(self):
        qc = self._make_circuit(1)
        qc.h(0)
        compiled = qc.compile()
        assert compiled is not qc

    def test_double_cx_cancellation(self):
        qc = self._make_circuit(2)
        qc.cx(0, 1)
        qc.cx(0, 1)
        compiled = qc.compile()
        assert compiled.depth == 0


# ---------------------------------------------------------------
# Introspection / utility tests
# ---------------------------------------------------------------

class TestIntrospection:
    def test_depth(self):
        qc = QuantumCircuit(QuantumRegister(2), ClassicalRegister(2))
        qc.h(0)
        qc.cx(0, 1)
        assert qc.depth == 2

    def test_depth_excludes_measurements(self):
        qc = QuantumCircuit(QuantumRegister(1), ClassicalRegister(1))
        qc.h(0)
        qc.measure(0, 0)
        assert qc.depth == 1

    def test_gate_count(self):
        qc = QuantumCircuit(QuantumRegister(2), ClassicalRegister(2))
        qc.h(0)
        qc.h(1)
        qc.cx(0, 1)
        assert qc.gate_count == {"h": 2, "cx": 1}

    def test_copy_is_independent(self):
        qc = QuantumCircuit(QuantumRegister(1), ClassicalRegister(1))
        qc.h(0)
        qc2 = qc.copy()
        qc2.x(0)
        assert qc.depth == 1
        assert qc2.depth == 2

    def test_reset(self):
        qc = QuantumCircuit(QuantumRegister(1), ClassicalRegister(1))
        qc.h(0)
        qc.reset()
        assert qc.depth == 0
        sv = qc.get_statevector()
        assert np.isclose(sv[0], 1.0)

    def test_operations_returns_copy(self):
        qc = QuantumCircuit(QuantumRegister(1), ClassicalRegister(1))
        qc.h(0)
        ops = qc.operations
        ops.clear()
        assert qc.depth == 1  # original unchanged


# ---------------------------------------------------------------
# 4-qubit circuit (issue requirement: basic 4-qubit test)
# ---------------------------------------------------------------

class TestFourQubitCircuit:
    """Validates the specific 4-qubit circuit described in the issue."""

    def test_issue_example_circuit(self):
        """Reproduce the circuit from the issue: 4 qubits, 4 classical bits,
        H on q0, CNOT q0→q1, measure all."""
        qreg_q = QuantumRegister(4, "q")
        creg_c = ClassicalRegister(4, "c")
        circuit = QuantumCircuit(qreg_q, creg_c)

        circuit.h(0)
        circuit.cx(0, 1)
        circuit.measure(qreg_q, creg_c)

        counts = circuit.simulate(shots=1000)
        for bitstring in counts:
            # q0 and q1 are entangled, q2 and q3 stay 0
            assert bitstring[2:] == "00"
            assert bitstring[:2] in ("00", "11")

    def test_ghz_state(self):
        """Create a 4-qubit GHZ state: (|0000⟩ + |1111⟩)/√2."""
        qreg = QuantumRegister(4, "q")
        creg = ClassicalRegister(4, "c")
        qc = QuantumCircuit(qreg, creg)

        qc.h(0)
        qc.cx(0, 1)
        qc.cx(1, 2)
        qc.cx(2, 3)
        qc.measure(qreg, creg)

        counts = qc.simulate(shots=2000)
        for bitstring in counts:
            assert bitstring in ("0000", "1111")
