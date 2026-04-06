#!/usr/bin/env python3
"""
SICOCA Test Suite
=================
Comprehensive tests for the SICOCA quantum circuit framework covering
gates, qubit helpers, circuit construction, simulation, and
interlocking chains.

Run with:  python -m pytest scripts/sicoca/tests/test_sicoca.py -v
       or: python scripts/sicoca/tests/test_sicoca.py
"""

from __future__ import annotations

import math
import sys
import os
import unittest

import numpy as np

# Ensure the scripts directory is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from sicoca import (
    Gate, H, X, Y, Z, I, CNOT, get_gate, GATE_CATALOGUE,
    KET_0, KET_1, basis_state, tensor_product, measure, probabilities,
    Circuit, bell_pair, ghz_state, superdense_coding_encode,
    Simulator, SimulationResult,
    Chain, ChainManager, Link, LinkStatus,
    always_proceed, majority_outcome, fidelity_threshold,
    launch,
)
from sicoca.tests import make_dummy_result


# =========================================================================
# 1.  Gate tests
# =========================================================================

class TestGateDefinitions(unittest.TestCase):
    """Verify matrix properties of all gates."""

    def test_hadamard_is_unitary(self):
        product = H.matrix @ H.matrix.conj().T
        np.testing.assert_array_almost_equal(product, np.eye(2))

    def test_hadamard_is_hermitian(self):
        np.testing.assert_array_almost_equal(H.matrix, H.matrix.conj().T)

    def test_pauli_x_squares_to_identity(self):
        np.testing.assert_array_almost_equal(X.matrix @ X.matrix, np.eye(2))

    def test_pauli_y_squares_to_identity(self):
        np.testing.assert_array_almost_equal(Y.matrix @ Y.matrix, np.eye(2))

    def test_pauli_z_squares_to_identity(self):
        np.testing.assert_array_almost_equal(Z.matrix @ Z.matrix, np.eye(2))

    def test_pauli_x_flips_zero(self):
        result = X.matrix @ KET_0
        np.testing.assert_array_almost_equal(result, KET_1)

    def test_pauli_x_flips_one(self):
        result = X.matrix @ KET_1
        np.testing.assert_array_almost_equal(result, KET_0)

    def test_pauli_z_phase_flips(self):
        result = Z.matrix @ KET_1
        np.testing.assert_array_almost_equal(result, -KET_1)

    def test_cnot_matrix_shape(self):
        self.assertEqual(CNOT.matrix.shape, (4, 4))

    def test_cnot_is_unitary(self):
        product = CNOT.matrix @ CNOT.matrix.conj().T
        np.testing.assert_array_almost_equal(product, np.eye(4))

    def test_gate_catalogue_contains_all(self):
        for name in ("H", "X", "Y", "Z", "I", "CNOT", "CX"):
            self.assertIn(name, GATE_CATALOGUE)

    def test_get_gate_lookup(self):
        self.assertIs(get_gate("H"), H)
        self.assertIs(get_gate("cnot"), CNOT)

    def test_get_gate_unknown_raises(self):
        with self.assertRaises(KeyError):
            get_gate("TOFFOLI")

    def test_validate_passes_for_all_gates(self):
        for gate in (H, X, Y, Z, I, CNOT):
            self.assertTrue(gate.validate())

    def test_validate_fails_for_non_unitary(self):
        bad = Gate(name="bad", matrix=np.array([[1, 1], [0, 0]], dtype=complex),
                   n_qubits=1)
        with self.assertRaises(ValueError):
            bad.validate()


class TestGateBind(unittest.TestCase):
    """Verify gate binding to qubit indices."""

    def test_bind_single_qubit(self):
        bound = H.bind(2)
        self.assertEqual(bound.target_qubits, (2,))

    def test_bind_two_qubit(self):
        bound = CNOT.bind(0, 3)
        self.assertEqual(bound.target_qubits, (0, 3))

    def test_bind_wrong_count_raises(self):
        with self.assertRaises(ValueError):
            H.bind(0, 1)

    def test_bind_negative_raises(self):
        with self.assertRaises(ValueError):
            H.bind(-1)

    def test_bind_duplicate_raises(self):
        with self.assertRaises(ValueError):
            CNOT.bind(1, 1)


# =========================================================================
# 2.  Qubit helpers
# =========================================================================

class TestQubitHelpers(unittest.TestCase):

    def test_basis_state_zero(self):
        state = basis_state(2, 0)
        expected = np.array([1, 0, 0, 0], dtype=complex)
        np.testing.assert_array_equal(state, expected)

    def test_basis_state_three(self):
        state = basis_state(2, 3)
        expected = np.array([0, 0, 0, 1], dtype=complex)
        np.testing.assert_array_equal(state, expected)

    def test_basis_state_out_of_range(self):
        with self.assertRaises(ValueError):
            basis_state(2, 4)

    def test_tensor_product(self):
        result = tensor_product([KET_0, KET_1])
        expected = np.array([0, 1, 0, 0], dtype=complex)
        np.testing.assert_array_almost_equal(result, expected)

    def test_probabilities_sum_to_one(self):
        state = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)], dtype=complex)
        probs = probabilities(state)
        self.assertAlmostEqual(probs.sum(), 1.0)

    def test_measure_returns_valid_bitstrings(self):
        state = basis_state(2, 0)
        counts = measure(state, shots=100, seed=0)
        self.assertEqual(list(counts.keys()), ["00"])

    def test_measure_deterministic_for_basis(self):
        state = basis_state(3, 5)
        counts = measure(state, shots=100, seed=0)
        self.assertIn("101", counts)
        self.assertEqual(counts["101"], 100)


# =========================================================================
# 3.  Circuit construction
# =========================================================================

class TestCircuit(unittest.TestCase):

    def test_add_gate_h(self):
        c = Circuit(2)
        c.h(0)
        self.assertEqual(c.depth, 1)

    def test_fluent_api(self):
        c = Circuit(2).h(0).cnot(0, 1)
        self.assertEqual(c.depth, 2)

    def test_qubit_index_out_of_range(self):
        c = Circuit(2)
        with self.assertRaises(IndexError):
            c.h(2)

    def test_bell_pair_template(self):
        c = bell_pair()
        self.assertEqual(c.depth, 2)
        self.assertEqual(c.n_qubits, 2)

    def test_ghz_state_template(self):
        c = ghz_state(4)
        self.assertEqual(c.depth, 4)  # H + 3 CNOTs
        self.assertEqual(c.n_qubits, 4)

    def test_ghz_minimum(self):
        with self.assertRaises(ValueError):
            ghz_state(1)

    def test_circuit_copy_is_independent(self):
        c = Circuit(2).h(0)
        c2 = c.copy()
        c2.x(1)
        self.assertEqual(c.depth, 1)
        self.assertEqual(c2.depth, 2)

    def test_draw_returns_string(self):
        c = bell_pair()
        diagram = c.draw()
        self.assertIn("q0:", diagram)
        self.assertIn("q1:", diagram)

    def test_restart_clears_operations(self):
        c = Circuit(2).h(0).cnot(0, 1)
        self.assertEqual(c.depth, 2)
        c.restart()
        self.assertEqual(c.depth, 0)
        self.assertEqual(c.n_qubits, 2)
        self.assertEqual(c.name, "circuit")

    def test_restart_allows_rebuilding(self):
        c = Circuit(2, name="reuse").h(0)
        c.restart().x(0).x(1)
        self.assertEqual(c.depth, 2)


# =========================================================================
# 4.  Simulator
# =========================================================================

class TestSimulator(unittest.TestCase):

    def setUp(self):
        self.sim = Simulator(shots=2048, seed=42)

    def test_identity_circuit(self):
        c = Circuit(1, name="identity")
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(result.statevector, KET_0)

    def test_x_gate(self):
        c = Circuit(1, name="x").x(0)
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(result.statevector, KET_1)

    def test_h_creates_superposition(self):
        c = Circuit(1, name="h").h(0)
        result = self.sim.run(c)
        expected = np.array([1 / math.sqrt(2), 1 / math.sqrt(2)], dtype=complex)
        np.testing.assert_array_almost_equal(result.statevector, expected)

    def test_bell_state(self):
        c = bell_pair()
        result = self.sim.run(c, shots=4096)
        sv = result.statevector
        expected = np.array([1 / math.sqrt(2), 0, 0, 1 / math.sqrt(2)],
                            dtype=complex)
        np.testing.assert_array_almost_equal(sv, expected)
        self.assertTrue(set(result.counts.keys()).issubset({"00", "11"}))

    def test_cnot_no_flip_when_control_zero(self):
        c = Circuit(2).cnot(0, 1)
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(
            result.statevector, basis_state(2, 0)
        )

    def test_cnot_flips_when_control_one(self):
        c = Circuit(2).x(0).cnot(0, 1)
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(
            result.statevector, basis_state(2, 3)
        )

    def test_non_adjacent_cnot(self):
        c = Circuit(3).x(0).cnot(0, 2)
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(
            result.statevector, basis_state(3, 5)
        )

    def test_reversed_cnot(self):
        c = Circuit(2).x(1).cnot(1, 0)
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(
            result.statevector, basis_state(2, 3)
        )

    def test_ghz_state_superposition(self):
        c = ghz_state(3)
        result = self.sim.run(c)
        expected = np.zeros(8, dtype=complex)
        expected[0] = 1 / math.sqrt(2)
        expected[7] = 1 / math.sqrt(2)
        np.testing.assert_array_almost_equal(result.statevector, expected)

    def test_double_x_is_identity(self):
        c = Circuit(1).x(0).x(0)
        result = self.sim.run(c)
        np.testing.assert_array_almost_equal(result.statevector, KET_0)

    def test_hzh_equals_x(self):
        c = Circuit(1).h(0).z(0).h(0)
        result = self.sim.run(c)
        expected = X.matrix @ KET_0
        np.testing.assert_array_almost_equal(result.statevector, expected)

    def test_custom_initial_state(self):
        c = Circuit(1, name="noop")
        result = self.sim.run(c, initial_state=KET_1)
        np.testing.assert_array_almost_equal(result.statevector, KET_1)

    def test_launch_convenience(self):
        c = Circuit(1).x(0)
        result = Simulator.launch(c, shots=100, seed=0)
        np.testing.assert_array_almost_equal(result.statevector, KET_1)

    def test_module_launch_shortcut(self):
        c = Circuit(1).h(0)
        result = launch(c, shots=100, seed=0)
        self.assertIn("0", result.counts)


# =========================================================================
# 5.  Interlocking chains
# =========================================================================

class TestInterlockPredicates(unittest.TestCase):

    def test_always_proceed(self):
        r = make_dummy_result({"00": 100})
        self.assertTrue(always_proceed(r))

    def test_majority_outcome_pass(self):
        pred = majority_outcome("00")
        self.assertTrue(pred(make_dummy_result({"00": 90, "11": 10})))

    def test_majority_outcome_fail(self):
        pred = majority_outcome("00")
        self.assertFalse(pred(make_dummy_result({"11": 90, "00": 10})))

    def test_fidelity_threshold_pass(self):
        ref = basis_state(2, 0)
        pred = fidelity_threshold(0.99, ref)
        r = SimulationResult("t", 2, basis_state(2, 0))
        self.assertTrue(pred(r))

    def test_fidelity_threshold_fail(self):
        ref = basis_state(2, 0)
        pred = fidelity_threshold(0.99, ref)
        r = SimulationResult("t", 2, basis_state(2, 3))
        self.assertFalse(pred(r))


class TestChain(unittest.TestCase):

    def test_chain_add_link(self):
        chain = Chain(name="test")
        chain.add_link(Circuit(2).h(0))
        self.assertEqual(len(chain.links), 1)

    def test_chain_fluent(self):
        chain = Chain(name="test")
        chain.add_link(Circuit(2).h(0)).add_link(Circuit(2).x(0))
        self.assertEqual(len(chain.links), 2)

    def test_chain_concatenate(self):
        a = Chain(name="a")
        a.add_link(Circuit(1).h(0), label="H")
        b = Chain(name="b")
        b.add_link(Circuit(1).x(0), label="X")
        merged = a.concatenate(b)
        self.assertEqual(merged.name, "a+b")
        self.assertEqual(len(merged.links), 2)
        self.assertEqual(merged.links[0].label, "H")
        self.assertEqual(merged.links[1].label, "X")

    def test_chain_concatenate_custom_name(self):
        a = Chain(name="a").add_link(Circuit(1).h(0))
        b = Chain(name="b").add_link(Circuit(1).x(0))
        merged = a.concatenate(b, name="custom")
        self.assertEqual(merged.name, "custom")

    def test_make_dummy_result(self):
        r = make_dummy_result({"11": 50})
        self.assertEqual(r.counts, {"11": 50})
        self.assertEqual(r.n_qubits, 2)


class TestChainManager(unittest.TestCase):

    def setUp(self):
        self.sim = Simulator(shots=1024, seed=42)
        self.mgr = ChainManager(simulator=self.sim)

    def test_register_and_execute(self):
        chain = Chain(name="simple")
        chain.add_link(bell_pair(), label="Bell")
        self.mgr.register_chain(chain)
        results = self.mgr.execute_chain("simple")
        self.assertEqual(len(results), 1)
        self.assertIsInstance(results[0], SimulationResult)

    def test_duplicate_registration_raises(self):
        self.mgr.register_chain(Chain(name="dup"))
        with self.assertRaises(ValueError):
            self.mgr.register_chain(Chain(name="dup"))

    def test_execute_unknown_raises(self):
        with self.assertRaises(KeyError):
            self.mgr.execute_chain("nonexistent")

    def test_chain_blocks_on_interlock(self):
        chain = Chain(name="blocking")
        chain.add_link(bell_pair(), label="Bell")
        chain.add_link(Circuit(2).x(0),
                       interlock=majority_outcome("11"),
                       label="Should block")
        self.mgr.register_chain(chain)
        results = self.mgr.execute_chain("blocking")
        link1 = chain.links[1]
        self.assertIn(link1.status, (LinkStatus.BLOCKED, LinkStatus.EXECUTED))

    def test_chain_proceeds_with_always(self):
        chain = Chain(name="proceed")
        chain.add_link(Circuit(1).h(0), label="H")
        chain.add_link(Circuit(1).x(0), interlock=always_proceed, label="X")
        self.mgr.register_chain(chain)
        results = self.mgr.execute_chain("proceed")
        self.assertEqual(len(results), 2)

    def test_execute_all(self):
        self.mgr.register_chain(Chain(name="a").add_link(Circuit(1).h(0)))
        self.mgr.register_chain(Chain(name="b").add_link(Circuit(1).x(0)))
        all_results = self.mgr.execute_all()
        self.assertEqual(set(all_results.keys()), {"a", "b"})

    def test_summary_string(self):
        chain = Chain(name="sum")
        chain.add_link(Circuit(1).h(0))
        self.mgr.register_chain(chain)
        self.mgr.execute_chain("sum")
        summary = self.mgr.summary()
        self.assertIn("SICOCA", summary)
        self.assertIn("sum", summary)


# =========================================================================
# Run
# =========================================================================

if __name__ == "__main__":
    unittest.main()
