"""Local report reader tool for PDF, DOCX, TXT, and Markdown files."""

from __future__ import annotations

from pathlib import Path
from typing import Type

import docx2txt
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from pypdf import PdfReader


class ReportReaderInput(BaseModel):
    reports_dir: str = Field(..., description="Directory containing report files.")


class ReportReaderTool(BaseTool):
    name: str = "Report Reader Tool"
    description: str = (
        "Read all PDF, DOCX, TXT, and Markdown reports from a directory and "
        "return extracted plain text. This tool does not call external APIs."
    )
    args_schema: Type[BaseModel] = ReportReaderInput

    def _run(self, reports_dir: str) -> str:
        folder = Path(reports_dir).resolve()

        if not folder.exists():
            return f"[ERROR] reports_dir does not exist: {folder}"

        files = [
            p
            for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in {".pdf", ".docx", ".txt", ".md"}
        ]

        if not files:
            return f"[ERROR] No readable report files found in: {folder}"

        outputs = []
        for file in sorted(files):
            suffix = file.suffix.lower()
            outputs.append(f"\n\n# Report File: {file.name}\n")

            try:
                if suffix == ".pdf":
                    reader = PdfReader(str(file))
                    text_parts = []
                    for i, page in enumerate(reader.pages):
                        text = page.extract_text() or ""
                        text_parts.append(f"\n\n## Page {i + 1}\n{text}")
                    outputs.append("\n".join(text_parts))

                elif suffix == ".docx":
                    outputs.append(docx2txt.process(str(file)))

                elif suffix in {".txt", ".md"}:
                    outputs.append(file.read_text(encoding="utf-8", errors="ignore"))

            except Exception as e:  # noqa: BLE001
                outputs.append(f"[ERROR] Failed to read {file.name}: {e}")

        return "\n".join(outputs)
