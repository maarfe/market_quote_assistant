"""Unit tests for the result export service."""

import json

from app.services.result_export_service import ResultExportService


def test_export_json_should_write_payload_to_file(tmp_path):
    service = ResultExportService()
    output_path = tmp_path / "output" / "result.json"
    payload = {
        "status": "ok",
        "total_cost": 58.88,
    }

    result = service.export_json(output_path, payload)

    assert result == output_path
    assert output_path.exists()

    written_payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert written_payload == payload


def test_export_json_should_create_parent_directories_when_needed(tmp_path):
    service = ResultExportService()
    output_path = tmp_path / "nested" / "dir" / "result.json"

    service.export_json(output_path, {"status": "ok"})

    assert output_path.exists()
    assert output_path.parent.exists()