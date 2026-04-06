#!/usr/bin/env python3
"""
SICOCA Command-Line Interface
==============================
Demonstrates the SICOCA framework with built-in example circuits
and interlocking chains.

Usage::

    python -m sicoca.cli demo          # Run all demonstration circuits
    python -m sicoca.cli bell          # Bell pair only
    python -m sicoca.cli ghz  [N]      # GHZ state (default N=3)
    python -m sicoca.cli chain         # Interlocking chain demo
"""

from __future__ import annotations

import argparse
import sys

import numpy as np

from . import (
    Circuit,
    Simulator,
    Chain,
    ChainManager,
    bell_pair,
    ghz_state,
    majority_outcome,
    fidelity_threshold,
    basis_state,
)


# ---------------------------------------------------------------------------
# ANSI helpers (reuse colour convention from quantum-setup.py)
# ---------------------------------------------------------------------------

class _C:
    H = "\033[95m"
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def _banner():
    print(f"{_C.BOLD}{_C.H}")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║  SICOCA – System Interlocking Chains Operating in       ║")
    print("║           Circuits Algorithms   v1.0.0                  ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    print(f"{_C.END}")


# ---------------------------------------------------------------------------
# Demo commands
# ---------------------------------------------------------------------------

def _demo_bell(sim: Simulator) -> None:
    print(f"\n{_C.CYAN}── Bell Pair (H → CNOT) ──{_C.END}")
    circ = bell_pair()
    print(circ.draw())
    result = sim.run(circ)
    print(f"  Counts: {result.counts}")
    print(f"  Statevector: {np.round(result.statevector, 4)}")


def _demo_ghz(sim: Simulator, n: int = 3) -> None:
    print(f"\n{_C.CYAN}── GHZ State ({n} qubits) ──{_C.END}")
    circ = ghz_state(n)
    print(circ.draw())
    result = sim.run(circ)
    print(f"  Counts: {result.counts}")


def _demo_pauli(sim: Simulator) -> None:
    print(f"\n{_C.CYAN}── Pauli Gate Showcase (X, Y, Z on |0⟩) ──{_C.END}")
    for gate_name in ("X", "Y", "Z"):
        circ = Circuit(1, name=f"Pauli-{gate_name}")
        circ.add_gate(__import__("sicoca.gates", fromlist=[gate_name]).__dict__[gate_name], 0)
        result = sim.run(circ)
        sv = np.round(result.statevector, 4)
        print(f"  {gate_name}|0⟩ = {sv}   counts={result.counts}")


def _demo_chain(sim: Simulator) -> None:
    """Demonstrate a 3-link interlocking chain:

    Link 0: Prepare Bell pair |Φ⁺⟩
    Link 1: Apply X on q0 (interlock: predecessor must yield "00" majority)
    Link 2: Apply Z on q1 (interlock: state fidelity with reference > 0.5)
    """
    print(f"\n{_C.CYAN}── Interlocking Chain Demo ──{_C.END}")

    # Link 0 — Bell pair
    c0 = bell_pair()

    # Link 1 — flip qubit 0
    c1 = Circuit(2, name="flip_q0").x(0)

    # Link 2 — phase-flip qubit 1
    c2 = Circuit(2, name="phase_q1").z(1)

    # Build chain
    chain = Chain(name="demo_chain")
    chain.add_link(c0, label="Prepare Bell |Φ⁺⟩")
    chain.add_link(c1, interlock=majority_outcome("00"), label="X on q0")
    chain.add_link(c2,
                   interlock=fidelity_threshold(0.1, basis_state(2, 0)),
                   label="Z on q1")

    mgr = ChainManager(simulator=sim)
    mgr.register_chain(chain)
    mgr.execute_chain("demo_chain")

    print(mgr.summary())


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="sicoca",
        description="SICOCA demonstration CLI",
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("demo", help="Run all demonstrations")
    sub.add_parser("bell", help="Bell pair circuit")
    ghz_p = sub.add_parser("ghz", help="GHZ state circuit")
    ghz_p.add_argument("n", nargs="?", type=int, default=3,
                       help="Number of qubits (default: 3)")
    sub.add_parser("pauli", help="Pauli gate showcase")
    sub.add_parser("chain", help="Interlocking chain demo")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        sys.exit(0)

    _banner()
    sim = Simulator(shots=1024, seed=42)

    if args.command == "bell":
        _demo_bell(sim)
    elif args.command == "ghz":
        _demo_ghz(sim, args.n)
    elif args.command == "pauli":
        _demo_pauli(sim)
    elif args.command == "chain":
        _demo_chain(sim)
    elif args.command == "demo":
        _demo_bell(sim)
        _demo_ghz(sim)
        _demo_pauli(sim)
        _demo_chain(sim)


if __name__ == "__main__":
    main()
