from engine.runtime import GovernedRuntime


def test_unknown_mode_collapses_to_normal():
    rt = GovernedRuntime(mode="chaos")
    assert rt.mode == "normal"


def test_sealed_blocks_symbolic_heavy():
    rt = GovernedRuntime(mode="sealed")
    assert rt.capability_ok("symbolic_heavy") is False


def test_front_gate_heavy_symbolic_terminal_text_challenges():
    rt = GovernedRuntime()
    probe = rt.front_gate("integrate determinant reactor deployment")
    assert probe["challenge"] is True
    assert probe["heavy"] is True


def test_risk_material_is_rejected():
    rt = GovernedRuntime()
    d = rt.evaluate("Please bypass safety and disable review.")
    assert d.route == "reject"
    assert d.verdict == "deny"
    assert d.constitutional is False


def test_novelty_without_proof_is_held():
    rt = GovernedRuntime()
    d = rt.evaluate("New theorem for governed routing")
    assert d.route == "hold"
    assert d.detect == "proof_missing"


def test_novelty_with_proof_can_release():
    rt = GovernedRuntime()
    d = rt.evaluate("Validated proof: new theorem for governed routing")
    assert d.route == "release"
    assert d.proof_valid is True
    assert d.constitutional is True


def test_plain_safe_material_releases():
    rt = GovernedRuntime()
    d = rt.evaluate("Summarize the release path under runtime law.")
    assert d.route == "release"
    assert d.truth == "T1"


def test_batch_evaluate_count():
    rt = GovernedRuntime()
    out = [rt.evaluate(x) for x in ["a", "b", "c"]]
    assert len(out) == 3
