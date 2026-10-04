from tickerflow.services.case_service import DemoRunRequest, run_case


def test_run_uses_one_fixture_and_real_row_decisions() -> None:
    result = run_case(DemoRunRequest())
    assert result.report.input_rows == 8
    assert result.report.valid_rows == 6
    assert result.report.quarantined_rows == 2
    assert result.rows[1].rule_codes == ["duplicate_key"]
    assert result.rows[2].disposition == "quarantined"
    assert result.bars[1].contributor_ids == [4]
    assert result.bars[1].volume == 300
    assert result.query[0].source == "demo:duplicates:v1"
    assert run_case(DemoRunRequest()) == result


def test_raw_invalid_values_and_overlapping_rules_are_inspectable() -> None:
    result = run_case(DemoRunRequest(case_id="ranges"))
    assert result.report.valid_rows == 4
    assert result.report.quarantined_rows == 3
    row = result.rows[2]
    assert row.original["close"] == "NaN" and row.original["volume"] == "Infinity"
    assert row.normalized["close"] is None and row.normalized["volume"] is None
    assert "non_finite_numeric_value" in row.rule_codes
    assert sum(i.count for i in result.report.issues) > result.report.quarantined_rows


def test_committed_cases_match_hand_checked_manifest() -> None:
    import json
    from pathlib import Path

    manifest = json.loads((Path(__file__).parents[1] / "fixtures/demo_expected.json").read_text())
    for case, expected in manifest.items():
        request = DemoRunRequest.model_validate({"case_id": case})
        result = run_case(request)
        assert result.report.input_rows == expected["input"]
        assert result.report.valid_rows == expected["accepted"]
        assert result.report.quarantined_rows == expected["quarantined"]
        assert [b.contributor_ids for b in result.bars] == expected["aapl_hourly_contributors"]
