#!/usr/bin/env python3
"""Post-process anonymous Health Policy submission DOCX for double-blind review."""

from __future__ import annotations

from pathlib import Path

from docx import Document

INPUT = Path("10Manuscript_health_policy_submission_v1_anonymous.docx")
OUTPUT = INPUT

AUTHOR_CONTRIB_REPLACEMENT = (
    "[Author contributions are provided on the separate title page "
    "for double-anonymized peer review.]"
)

# GitHub URL with username is omitted during double-blind review (Zenodo DOI only).
DATA_AVAIL_BLINDED = (
    "The NDB Open Data used in this analysis are publicly available from the "
    "Ministry of Health, Labour and Welfare of Japan "
    "(https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html). "
    "Analysis code is archived on Zenodo "
    "(https://doi.org/10.5281/zenodo.20756030). "
    "A public GitHub repository link will be provided upon acceptance."
)

DATA_AVAIL_IDENTIFYING_MARKERS = (
    "github.com/haruki00430",
    "Haruki Saito:",
    "Tetsuya Ohira:",
)


def main() -> None:
    doc = Document(INPUT)
    changed: list[str] = []

    for par in doc.paragraphs:
        text = par.text.strip()

        if text.startswith("Objective:"):
            for run in par.runs:
                if run.text.startswith("Objective:"):
                    run.text = run.text.replace("Objective:", "Objectives:", 1)
                    changed.append("Abstract: Objective → Objectives")
                    break

        if text.startswith("Haruki Saito:") or text.startswith("Tetsuya Ohira:"):
            for run in par.runs:
                run.text = ""
            changed.append(f"Removed identifying Author Contributions line: {text[:40]}...")

        if text == "Author Contributions":
            for run in par.runs:
                run.text = AUTHOR_CONTRIB_REPLACEMENT
            changed.append("Author Contributions section anonymized")

        if any(m in text for m in DATA_AVAIL_IDENTIFYING_MARKERS) or (
            "zenodo" in text.lower() and "github.com" in text.lower()
        ):
            for run in par.runs:
                run.text = ""
            if par.runs:
                par.runs[0].text = DATA_AVAIL_BLINDED
            else:
                par.add_run(DATA_AVAIL_BLINDED)
            changed.append("Data Availability blinded (Zenodo only)")

    doc.save(OUTPUT)
    print(f"Saved: {OUTPUT}")
    for item in changed:
        print(f"  - {item}")


if __name__ == "__main__":
    main()
