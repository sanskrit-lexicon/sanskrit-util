# -*- coding: utf-8 -*-
"""H6979 — the data-layer sidecar gate.

The point of this file is the NEGATIVE cases: a gate that only has a passing
fixture has not been tested (decision #18). Every refusal below is a way a real
layer could be registered without a consumer, without provenance, or as dormant
with nobody to wake it up.
"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..'))

import sanskrit_util as su  # noqa: E402
from sanskrit_util.sidecar import SidecarError  # noqa: E402


def good_payload(**over):
    payload = {
        "layer": "dcs-compound-dictionary",
        "made_by": "human+ai",
        "model": "claude-sonnet-5",
        "handoff": "H6979",
        "consumers": [{"kind": "repo", "id": "kosha",
                       "use": "names.csv join"}],
        "status": "active",
        "novelty": "same compounds as DCS, but keyed for the kosha names.csv join",
    }
    payload.update(over)
    return payload


def problems_of(payload):
    return su.validate_sidecar(payload)


# ---------- positive ----------

def test_valid_active_sidecar_passes():
    assert problems_of(good_payload()) == []


def test_valid_dormant_sidecar_passes_without_consumers():
    assert problems_of(good_payload(consumers=[], status="dormant",
                                    owner="MG", review_after="2027-01-18")) == []


def test_write_sidecar_roundtrip(tmp_path):
    target = tmp_path / "layer.meta.json"
    written = su.write_sidecar(target, good_payload())
    assert written == target
    payload, problems = su.load_sidecar(target)
    assert problems == []
    assert payload["layer"] == "dcs-compound-dictionary"
    assert json.loads(target.read_text(encoding="utf-8"))["made_by"] == "human+ai"


def test_write_sidecar_into_directory_names_file_after_layer(tmp_path):
    written = su.write_sidecar(tmp_path, good_payload())
    assert written == tmp_path / "dcs-compound-dictionary.meta.json"
    assert written.exists()


def test_dry_run_writes_nothing(tmp_path):
    target = tmp_path / "layer.meta.json"
    assert su.write_sidecar(target, good_payload(), dry_run=True) == target
    assert not target.exists()


def test_sidecar_path_for_artifact_and_layer(tmp_path):
    artifact = tmp_path / "union_headwords.tsv"
    assert su.sidecar_path_for(artifact) == tmp_path / "union_headwords.tsv.meta.json"
    assert su.sidecar_path_for(artifact, layer="union-headwords") == \
        tmp_path / "union-headwords.meta.json"
    with pytest.raises(SidecarError):
        su.sidecar_path_for(artifact, layer="a/b")


# ---------- negative: the gate must actually refuse ----------

def test_refuses_without_made_by():
    payload = good_payload()
    del payload["made_by"]
    problems = problems_of(payload)
    assert any("made_by" in p for p in problems)
    with pytest.raises(SidecarError):
        su.write_sidecar("/nonexistent/dir/x.meta.json", payload)


def test_refuses_blank_made_by():
    assert any("made_by" in p for p in problems_of(good_payload(made_by="  ")))


def test_refuses_unknown_made_by_value():
    assert any("made_by" in p for p in problems_of(good_payload(made_by="robot")))


def test_refuses_no_consumers_and_not_dormant():
    problems = problems_of(good_payload(consumers=[]))
    assert any("no consumers" in p for p in problems)


def test_refuses_dormant_without_owner():
    problems = problems_of(good_payload(consumers=[], status="dormant",
                                        review_after="2027-01-18"))
    assert any("owner" in p for p in problems)


def test_refuses_dormant_without_review_after():
    problems = problems_of(good_payload(consumers=[], status="dormant",
                                        owner="MG"))
    assert any("review_after" in p for p in problems)


def test_refuses_dormant_with_impossible_date():
    problems = problems_of(good_payload(consumers=[], status="dormant",
                                        owner="MG", review_after="2027-13-45"))
    assert any("review_after" in p for p in problems)


def test_refuses_without_novelty():
    assert any("novelty" in p for p in problems_of(good_payload(novelty="")))


def test_refuses_bad_status():
    assert any("status" in p for p in problems_of(good_payload(status="live")))


def test_refuses_bad_consumer_kind():
    problems = problems_of(good_payload(
        consumers=[{"kind": "session", "id": "H6979"}]))
    assert any("consumers[0].kind" in p for p in problems)


def test_refuses_consumer_without_id():
    problems = problems_of(good_payload(consumers=[{"kind": "repo"}]))
    assert any("consumers[0].id" in p for p in problems)


def test_refuses_bad_handoff():
    assert any("handoff" in p for p in problems_of(good_payload(handoff="6979")))


def test_refuses_human_gold_without_roundtrip():
    problems = problems_of(good_payload(human_gold=True))
    assert any("roundtrip" in p for p in problems)


def test_refuses_human_gold_roundtrip_row_loss():
    problems = problems_of(good_payload(
        human_gold=True, roundtrip={"checked": True, "rows_in": 10, "rows_out": 9}))
    assert any("lost rows" in p for p in problems)


def test_refuses_unchecked_roundtrip():
    problems = problems_of(good_payload(
        roundtrip={"checked": False, "rows_in": 10, "rows_out": 10}))
    assert any("checked" in p for p in problems)


def test_refuses_non_dict_payload():
    assert problems_of(["not", "an", "object"])


def test_refusal_lists_every_problem_and_writes_nothing(tmp_path):
    target = tmp_path / "layer.meta.json"
    payload = {"layer": "", "consumers": []}
    with pytest.raises(SidecarError) as exc:
        su.write_sidecar(target, payload)
    assert len(exc.value.problems) >= 4
    assert not target.exists()
