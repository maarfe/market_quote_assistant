"""Services for exporting comparison results to external files."""

import json
from pathlib import Path
from typing import Any


class ResultExportService:
    """
    Export rendered result payloads to JSON files.
    """

    def export_json(self, file_path: str | Path, payload: dict[str, Any]) -> Path:
        """
        Write a JSON payload to the target file path.

        Args:
            file_path: Target path for the exported JSON file.
            payload: JSON-serializable payload to export.

        Returns:
            The resolved output path.
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        return path