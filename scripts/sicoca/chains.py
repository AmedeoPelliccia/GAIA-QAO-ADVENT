"""
SICOCA Interlocking Chains
===========================
System Interlocking Chains Operating in Circuits Algorithms

An **interlocking chain** is a directed acyclic graph (DAG) of
``Circuit`` nodes linked by dependency edges.  Each node's execution
may depend on measurement outcomes of predecessor nodes, enabling
classical feed-forward between quantum circuits.

Key concepts
------------
* **Link** – a single circuit together with an optional *interlock*
  predicate that must be satisfied before the circuit is executed.
* **Chain** – an ordered sequence of links executed from head to tail.
* **ChainManager** – orchestrates multiple named chains, checks for
  cycles, and drives execution through the ``Simulator``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Dict, List, Optional, Sequence

import numpy as np

from .circuit import Circuit
from .simulator import SimulationResult, Simulator

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Interlock predicate type
# ---------------------------------------------------------------------------
# An interlock is a callable that receives the *predecessor* result and
# returns True if the next link is allowed to proceed.
InterlockPredicate = Callable[[SimulationResult], bool]


def always_proceed(_result: SimulationResult) -> bool:
    """Default interlock: always allow the next link."""
    return True


def majority_outcome(target_bitstring: str) -> InterlockPredicate:
    """Interlock that passes when *target_bitstring* is the most frequent
    measurement outcome of the predecessor circuit."""
    def _check(result: SimulationResult) -> bool:
        if not result.counts:
            return False
        best = max(result.counts, key=result.counts.get)  # type: ignore[arg-type]
        return best == target_bitstring
    return _check


def fidelity_threshold(min_fidelity: float,
                       reference_state: np.ndarray) -> InterlockPredicate:
    """Interlock that passes when the state fidelity with
    *reference_state* exceeds *min_fidelity*."""
    def _check(result: SimulationResult) -> bool:
        overlap = np.abs(np.vdot(reference_state, result.statevector)) ** 2
        return float(overlap) >= min_fidelity
    return _check


# ---------------------------------------------------------------------------
# Link & Chain
# ---------------------------------------------------------------------------

class LinkStatus(Enum):
    PENDING = auto()
    PASSED = auto()
    BLOCKED = auto()
    EXECUTED = auto()


@dataclass
class Link:
    """A single node in an interlocking chain.

    Attributes
    ----------
    circuit : Circuit
        The quantum circuit to execute at this link.
    interlock : InterlockPredicate
        A callable that decides whether this link may proceed based on
        the previous link's ``SimulationResult``.
    label : str
        Human-readable identifier for this link.
    status : LinkStatus
        Current execution status.
    result : SimulationResult or None
        Populated after successful execution.
    """

    circuit: Circuit
    interlock: InterlockPredicate = always_proceed
    label: str = ""
    status: LinkStatus = LinkStatus.PENDING
    result: Optional[SimulationResult] = None

    def __post_init__(self):
        if not self.label:
            self.label = self.circuit.name


@dataclass
class Chain:
    """An ordered sequence of :class:`Link` objects.

    Links are executed head-to-tail.  Each link's interlock predicate
    receives the result of the immediately preceding link.  If the
    interlock returns ``False`` the chain halts.
    """

    name: str
    links: List[Link] = field(default_factory=list)
    _executed: bool = field(default=False, repr=False)

    def add_link(self, circuit: Circuit,
                 interlock: InterlockPredicate = always_proceed,
                 label: str = "") -> "Chain":
        """Append a link to the chain (fluent API)."""
        self.links.append(Link(circuit=circuit, interlock=interlock,
                               label=label))
        return self

    @property
    def is_executed(self) -> bool:
        return self._executed

    @property
    def results(self) -> List[SimulationResult]:
        """Return simulation results of all executed links."""
        return [lnk.result for lnk in self.links if lnk.result is not None]


# ---------------------------------------------------------------------------
# Chain Manager
# ---------------------------------------------------------------------------

class ChainManager:
    """Orchestrates the execution of multiple interlocking chains.

    Parameters
    ----------
    simulator : Simulator or None
        The simulator back-end.  A default one is created if omitted.
    """

    def __init__(self, simulator: Simulator | None = None):
        self.simulator = simulator or Simulator()
        self._chains: Dict[str, Chain] = {}

    # -- registration ----------------------------------------------------------

    def register_chain(self, chain: Chain) -> None:
        """Register a chain with the manager."""
        if chain.name in self._chains:
            raise ValueError(f"Chain '{chain.name}' is already registered")
        self._chains[chain.name] = chain
        logger.info("Registered chain '%s' with %d link(s)",
                     chain.name, len(chain.links))

    def get_chain(self, name: str) -> Chain:
        """Look up a registered chain by name."""
        if name not in self._chains:
            raise KeyError(
                f"Chain '{name}' not found. "
                f"Registered: {list(self._chains.keys())}"
            )
        return self._chains[name]

    @property
    def chains(self) -> Dict[str, Chain]:
        """Return all registered chains."""
        return dict(self._chains)

    # -- execution -------------------------------------------------------------

    def execute_chain(self, name: str) -> List[SimulationResult]:
        """Execute a single chain by name.

        The chain's links are processed sequentially.  For each link
        (after the first) the interlock predicate is evaluated against
        the *previous* link's result.  If the predicate returns False
        the link is marked ``BLOCKED`` and execution halts.

        Returns
        -------
        list[SimulationResult]
            Results for every successfully executed link.
        """
        chain = self.get_chain(name)
        results: List[SimulationResult] = []
        prev_result: Optional[SimulationResult] = None

        logger.info("Executing chain '%s' (%d links)", name, len(chain.links))

        for idx, link in enumerate(chain.links):
            # Evaluate interlock (skip for the very first link)
            if prev_result is not None:
                if not link.interlock(prev_result):
                    link.status = LinkStatus.BLOCKED
                    logger.warning(
                        "Chain '%s' BLOCKED at link %d ('%s'): "
                        "interlock predicate failed",
                        name, idx, link.label,
                    )
                    break
                link.status = LinkStatus.PASSED

            # Execute circuit
            result = self.simulator.run(link.circuit)
            link.result = result
            link.status = LinkStatus.EXECUTED
            results.append(result)
            prev_result = result

            logger.info(
                "  Link %d ('%s') executed → top outcome: %s",
                idx,
                link.label,
                max(result.counts, key=result.counts.get)  # type: ignore[arg-type]
                if result.counts else "N/A",
            )

        chain._executed = True
        return results

    def execute_all(self) -> Dict[str, List[SimulationResult]]:
        """Execute every registered chain and return all results."""
        all_results: Dict[str, List[SimulationResult]] = {}
        for name in self._chains:
            all_results[name] = self.execute_chain(name)
        return all_results

    # -- reporting -------------------------------------------------------------

    def summary(self) -> str:
        """Return a human-readable summary of all chains and their status."""
        lines: list[str] = [
            "╔══════════════════════════════════════════════╗",
            "║    SICOCA – Interlocking Chains Summary      ║",
            "╚══════════════════════════════════════════════╝",
        ]
        for name, chain in self._chains.items():
            lines.append(f"\n● Chain: {name}  "
                         f"({'executed' if chain.is_executed else 'pending'})")
            for i, link in enumerate(chain.links):
                status_icon = {
                    LinkStatus.PENDING: "○",
                    LinkStatus.PASSED: "◑",
                    LinkStatus.BLOCKED: "✗",
                    LinkStatus.EXECUTED: "✓",
                }[link.status]
                extra = ""
                if link.result and link.result.counts:
                    top = max(link.result.counts,
                              key=link.result.counts.get)  # type: ignore[arg-type]
                    extra = f"  top=|{top}⟩"
                lines.append(
                    f"  {status_icon} Link {i}: {link.label} "
                    f"[{link.status.name}]{extra}"
                )
        return "\n".join(lines)
