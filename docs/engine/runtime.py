from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable


_ALLOWED_MODES = {"normal", "sealed", "siege"}
_HEAVY_SYMBOLS = ("integrate", "differentiate", "gradient", "determinant", "eigen", "inverse")
_RISK_TOKENS = ("override", "bypass", "weapon", "exploit", "disable safety")
_NOVELTY_TOKENS = ("new theorem", "new formula", "novel law", "invented rule")


@dataclass(frozen=True)
class Decision:
    route: str
    truth: str
    verdict: str
    answer: str
    detect: str
    proof_required: bool
    proof_valid: bool
    constitutional: bool
    metadata: Dict[str, Any]


@dataclass(frozen=True)
class ProofPacket:
    source_stage: str
    runtime_mode: str
    lineage: str
    proof_required: bool
    proof_valid: bool
    route: str
    truth: str

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class GovernedRuntime:
    def __init__(self, *, mode: str = "normal", cost_limit: int = 88) -> None:
        self.mode = self._normalize_mode(mode)
        self.cost_limit = int(cost_limit)

    @staticmethod
    def _normalize_mode(mode: str) -> str:
        mode = str(mode or "normal").strip().lower()
        return mode if mode in _ALLOWED_MODES else "normal"

    def set_mode(self, mode: str) -> str:
        self.mode = self._normalize_mode(mode)
        return self.mode

    def capability_ok(self, capability: str) -> bool:
        capability = str(capability or "")
        if self.mode == "sealed" and capability in {"rewrite", "symbolic_heavy", "work_admission"}:
            return False
        if self.mode == "siege" and capability in {"rewrite", "symbolic_heavy", "work_admission", "public_release"}:
            return False
        return True

    def front_cost(self, text: str) -> int:
        raw = " ".join(str(text or "").split())
        low = raw.lower()
        score = min(len(raw), 160)
        score += 3 * sum(raw.count(ch) for ch in "^*/[](),=")
        score += 2 * (raw.count("(") + raw.count("["))
        score += 12 * sum(tok in low for tok in _HEAVY_SYMBOLS)
        if any(tok in low for tok in ("deployment", "reactor", "terminal", "collapse")):
            score += 24
        return int(score)

    def front_gate(self, text: str) -> Dict[str, Any]:
        cost = self.front_cost(text)
        heavy = cost >= self.cost_limit
        repeated = text.lower().count("!") >= 3
        challenge = heavy or repeated or not self.capability_ok("symbolic_heavy")
        return {
            "cost": cost,
            "heavy": heavy,
            "repeated": repeated,
            "challenge": challenge,
        }

    def proof_packet(self, *, route: str, truth: str, proof_required: bool, proof_valid: bool) -> ProofPacket:
        return ProofPacket(
            source_stage="public_core",
            runtime_mode=self.mode,
            lineage="bounded_public_lineage",
            proof_required=bool(proof_required),
            proof_valid=bool(proof_valid),
            route=str(route),
            truth=str(truth),
        )

    def constitutional_ok(self, text: str, *, route: str, proof_valid: bool) -> bool:
        low = str(text or "").lower()
        if route not in {"release", "transform"}:
            return False
        if any(tok in low for tok in _RISK_TOKENS):
            return False
        if any(tok in low for tok in _NOVELTY_TOKENS) and not proof_valid:
            return False
        return len(low) <= 240

    def evaluate(self, text: str) -> Decision:
        gate = self.front_gate(text)
        low = str(text or "").lower()
        proof_required = any(tok in low for tok in _NOVELTY_TOKENS) or gate["heavy"]
        proof_valid = "proof:" in low or "validated" in low

        if any(tok in low for tok in _RISK_TOKENS):
            route, truth, verdict = "reject", "T0", "deny"
            answer = "Material rejected under runtime law."
            detect = "risk"
        elif gate["challenge"]:
            route, truth, verdict = "hold", "T0", "challenge"
            answer = "Material held pending challenge or proof."
            detect = "front_pressure"
        elif proof_required and not proof_valid:
            route, truth, verdict = "hold", "T0", "withhold"
            answer = "Material held until proof lineage is supplied."
            detect = "proof_missing"
        else:
            route, truth, verdict = "release", "T1", "allow"
            answer = "Material released under governed passage."
            detect = "lawful"

        constitutional = self.constitutional_ok(text, route=route, proof_valid=proof_valid)
        packet = self.proof_packet(route=route, truth=truth, proof_required=proof_required, proof_valid=proof_valid)
        return Decision(
            route=route,
            truth=truth,
            verdict=verdict,
            answer=answer,
            detect=detect,
            proof_required=proof_required,
            proof_valid=proof_valid,
            constitutional=constitutional,
            metadata={"front": gate, "proof_packet": packet.as_dict()},
        )


def batch_evaluate(runtime: GovernedRuntime, texts: Iterable[str]) -> list[Decision]:
    return [runtime.evaluate(text) for text in texts]
