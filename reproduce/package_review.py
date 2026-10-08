"""Check the assembled review and create its source/evidence archive.

This checks document integrity and audit coverage, not underlying theorem truth.
"""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import zipfile

import bibtexparser
from pypdf import PdfReader


PAPER = Path(__file__).resolve().parents[1]
WORKSPACE = PAPER.parents[1] if PAPER.parent.name == 'papers' else PAPER
AUDIT = PAPER / "audit"


def read_json(relative):
    return json.loads((PAPER / relative).read_text(encoding="utf-8"))


def save_json(relative, value):
    (PAPER / relative).write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    domains = {
        "research/root-references.bib": "research/root-evidence.json",
        "research/root-release.bib": "research/root-evidence.json",
        "research/arithmetic/references.bib": "research/arithmetic/evidence.json",
        "research/geometry-operators/references.bib": "research/geometry-operators/evidence.json",
        "research/combinatorics/references.bib": "research/combinatorics/evidence.json",
    }
    entries = bibtexparser.loads((PAPER / "references.bib").read_text(encoding="utf-8")).entries
    entry_map = {entry["ID"]: entry for entry in entries}
    keys = {entry["ID"] for entry in entries}
    assert len(entries) == len(keys), "Duplicate bibliography keys"
    tex_files = sorted(p for p in PAPER.rglob("*.tex") if "build" not in p.relative_to(PAPER).parts)
    tex = "\n".join(p.read_text(encoding="utf-8") for p in tex_files)
    cited = {
        key.strip()
        for match in re.finditer(r"\\cite\w*(?:\[[^\]]*\])*\{([^}]+)\}", tex)
        for key in match.group(1).split(",")
    }
    assert keys == cited, f"Citation mismatch: missing={cited-keys}, unused={keys-cited}"
    assert len(keys) > 25

    metadata = read_json("audit/reference-metadata.json")
    records = {r["key"]: r for r in metadata["records"]}
    assert set(records) == keys, "Metadata ledger does not cover bibliography"
    accepted = {"matched", "primary_record_in_research_ledger", "verified_primary_fallback", "resolved_title_completion"}
    assert all(r["metadata_status"] in accepted for r in records.values()), "Unresolved bibliographic identity"
    key_domains = {}
    for bibliography, ledger in domains.items():
        read_json(ledger)  # Require a valid, saved source-support ledger.
        for entry in bibtexparser.loads((PAPER / bibliography).read_text(encoding="utf-8")).entries:
            assert entry["ID"] not in key_domains, "Duplicate domain bibliography key"
            key_domains[entry["ID"]] = (bibliography, ledger)
    assert set(key_domains) == keys
    for record in records.values():
        if record.get("support_ledger"):
            read_json(record["support_ledger"])
    save_json("audit/reference-index.json", {
        "scope": "Links each cited source to its bibliographic identity check and domain source-support ledger; does not certify theorem validity.",
        "records": [
            {"key": key, "title": entry_map[key]["title"], "primary_url": records[key].get("primary_url"),
             "metadata_status": records[key]["metadata_status"],
             "bibliography": key_domains[key][0],
             "evidence_ledger": records[key].get("support_ledger", key_domains[key][1])}
            for key in sorted(keys)
        ],
    })

    root_tex = (PAPER / "main.tex").read_text(encoding="utf-8")
    disclosure = "OpenAI Codex agents contributed substantially to source discovery, literature synthesis, and mathematical exposition."
    normalized_root = " ".join(root_tex.split())
    assert normalized_root.count(disclosure) == 1
    assert normalized_root.index(disclosure) > normalized_root.index("\\section*{AI disclosure}")
    abstract = re.search(r"\\begin\{abstract\}([\s\S]*?)\\end\{abstract\}", root_tex).group(1)
    assert "Codex" not in abstract
    assert "fixed repository snapshot" not in tex.lower()

    pdf = PAPER / "openai-mathematical-frontiers.pdf"
    build = read_json("audit/build.json")
    assert not build["issues"]
    assert digest(pdf) == build["sha256"]
    assert len(PdfReader(pdf).pages) == build["pages"]
    examples = read_json("audit/illustrative-examples.json")
    assert all(examples[name]["passed"] for name in ("gf4", "jordan_example", "common_base_hessian",
                                                    "restricted_observable_chain", "finite_mesh", "shared_residue_pair"))
    resolution = read_json("audit/review-resolution.json")
    assert all(f["status"] == "resolved" for f in resolution["findings"])
    assert len(resolution["findings"]) >= 13
    for finding in resolution["findings"]:
        assert finding["current_sha256"] == digest(PAPER / finding["current_file"]), finding["id"]
    comparison = read_json("research/comparison-register.json")
    assert len(comparison["cases"]) == comparison["grouped_case_count"]
    for case in comparison["cases"]:
        assert set(case["baseline_keys"]) <= keys
    visual = read_json("audit/visual-review.json")
    assert visual["pdf_sha256"] == digest(pdf) and visual["pages_inspected"] == build["pages"]
    assert visual["issues"] == []
    ledgers = set(domains.values()) | {r["support_ledger"] for r in records.values() if r.get("support_ledger")}
    coverage = read_json("audit/citation-coverage.json")
    save_json("audit/final-audit.json", {
        "date": "2026-10-07", "paper_type": "Comparative narrative review",
        "pages": build["pages"], "grouped_case_studies": comparison["grouped_case_count"],
        "result_families": comparison["unique_family_count"],
        "cited_references": len(keys),
        "non_release_published_scholarly_references": coverage["non_release_published_scholarly_references"],
        "metadata_status_counts": dict(Counter(r["metadata_status"] for r in records.values())),
        "missing_citations": [], "unused_references": [], "duplicate_keys": [],
        "domain_evidence_ledgers": sorted(ledgers),
        "internal_findings_resolved": len(resolution["findings"]),
        "remaining_reviewer_opportunities": resolution.get("remaining_reviewer_opportunities", []),
        "deep_audit_report": resolution.get("deep_audit_report"),
        "build_issues": [], "pdf_sha256": digest(pdf),
        "visual_review": visual["method"],
        "novelty_assessment": "The magnitude of proposed conclusions, inherited machinery, and specific newly proposed bridges are assessed separately. Contrastive tests and a comparison register operationalize the synthesis.",
        "disclosure": "Approved disclosure appears once, in its dedicated section; absent from abstract.",
        "illustrative_examples_record": "audit/illustrative-examples.json",
        "validation_scope": "Bibliographic identity, source-statement comparison, elementary illustrative examples, internal exposition cross-review, compilation and rendered layout. Underlying release proofs and formal dependency builds are outside these checks.",
        "record_type": "Reproduction and internal-audit result; public release status is maintained in publication records.",
    })
    files = sorted(
        p for p in PAPER.rglob("*") if p.is_file()
        and p.relative_to(PAPER).parts[0] not in ('.git', 'output', 'tmp', 'dist')
        and not p.relative_to(PAPER).parts[0].startswith('.venv')
        and p.relative_to(PAPER).parts[0] not in ('venv', '.pytest_cache', '.mypy_cache', '.ruff_cache')
        and "build" not in p.relative_to(PAPER).parts
        and "__pycache__" not in p.relative_to(PAPER).parts
        and p.name not in ("artifact-manifest.json", "FILE_MANIFEST.json")
    )
    save_json("audit/artifact-manifest.json", {
        "scope": "Curated own-review sources, PDF, evidence ledgers and reproduction scripts; excludes build intermediates and downloaded third-party papers. Generated manifests are excluded to keep checksum dependencies acyclic.",
        "files": [{"path": p.relative_to(PAPER).as_posix(), "bytes": p.stat().st_size, "sha256": digest(p)} for p in files],
    })
    pdf_output = WORKSPACE / "output" / "pdf"
    pdf_output.mkdir(parents=True, exist_ok=True)
    shutil.copy2(pdf, pdf_output / pdf.name)
    release_output = WORKSPACE / "output" / "releases"
    release_output.mkdir(parents=True, exist_ok=True)
    archive = release_output / "openai-mathematical-frontiers-review.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files + [AUDIT / "artifact-manifest.json"]:
            z.write(path, PAPER.name + "/" + path.relative_to(PAPER).as_posix())
    print(json.dumps({"pdf": str(pdf), "pages": build["pages"], "references": len(keys),
                      "archive": str(archive), "archive_sha256": digest(archive)}, indent=2))


if __name__ == "__main__":
    main()
