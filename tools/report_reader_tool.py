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
    start_char: int = Field(
        default=0,
        description="Start character offset for the returned text chunk.",
    )
    max_chars: int = Field(
        default=12000,
        description="Maximum number of extracted text characters to return.",
    )


class ReportReaderTool(BaseTool):
    name: str = "Report Reader Tool"
    description: str = (
        "Read all PDF, DOCX, TXT, and Markdown reports from a directory and "
        "write extracted plain text to outputs/report_text_cache.md. Returns "
        "only a bounded text chunk to avoid flooding the terminal. This tool "
        "does not call external APIs."
    )
    args_schema: Type[BaseModel] = ReportReaderInput

    def _run(self, reports_dir: str, start_char: int = 0, max_chars: int = 12000) -> str:
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
        file_summaries = []
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
                    extracted = "\n".join(text_parts)
                    outputs.append(extracted)
                    file_summaries.append(
                        f"- {file.name}: PDF, pages={len(reader.pages)}, chars={len(extracted)}"
                    )

                elif suffix == ".docx":
                    extracted = docx2txt.process(str(file))
                    outputs.append(extracted)
                    file_summaries.append(f"- {file.name}: DOCX, chars={len(extracted)}")

                elif suffix in {".txt", ".md"}:
                    extracted = file.read_text(encoding="utf-8", errors="ignore")
                    outputs.append(extracted)
                    file_summaries.append(f"- {file.name}: {suffix[1:].upper()}, chars={len(extracted)}")

            except Exception as e:  # noqa: BLE001
                error = f"[ERROR] Failed to read {file.name}: {e}"
                outputs.append(error)
                file_summaries.append(f"- {file.name}: ERROR, {e}")

        full_text = "\n".join(outputs)
        cache_path = Path("outputs") / "report_text_cache.md"
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(full_text, encoding="utf-8")

        safe_start = max(0, min(start_char, len(full_text)))
        safe_max = max(1000, min(max_chars, 20000))
        end_char = min(safe_start + safe_max, len(full_text))
        chunk = full_text[safe_start:end_char]

        return (
            "Report extraction completed.\n"
            f"Cache file: {cache_path}\n"
            f"Total extracted characters: {len(full_text)}\n"
            f"Returned character range: {safe_start}-{end_char}\n"
            "Files:\n"
            + "\n".join(file_summaries)
            + "\n\n"
            "Text chunk:\n"
            f"{chunk}"
            + (
                "\n\n[TRUNCATED] Call this tool again with a larger start_char "
                "to read the next chunk."
                if end_char < len(full_text)
                else ""
            )
        )
