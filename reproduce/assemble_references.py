"""Assemble the independently researched bibliography and check citation coverage."""
from pathlib import Path
import json
import re
import bibtexparser
from bibtexparser.bwriter import BibTexWriter

PAPER = Path(__file__).resolve().parents[1]


def main():
    paths = sorted(PAPER.glob("research/root-*.bib"))
    paths += sorted(PAPER.glob("research/*/references.bib"))
    entries = {}
    for path in paths:
        database = bibtexparser.loads(path.read_text(encoding="utf-8"))
        for entry in database.entries:
            key = entry["ID"]
            if key in entries and entries[key] != entry:
                raise ValueError(f"Conflicting reference {key} in {path}")
            entries[key] = entry
    sources = [PAPER / "main.tex", PAPER / "overview.tex", PAPER / "synthesis.tex"]
    sources += sorted(PAPER.glob("research/*.tex"))
    sources += sorted(PAPER.glob("research/*/section.tex"))
    cited = set()
    for source in sources:
        text = source.read_text(encoding="utf-8")
        for match in re.finditer(r"\\cite\w*\*?(?:\[[^\]]*\]){0,2}\{([^}]+)\}", text):
            cited.update(key.strip() for key in match[1].split(","))
    missing = cited - entries.keys()
    if missing:
        raise ValueError(f"Missing references: {sorted(missing)}")
    database = bibtexparser.bibdatabase.BibDatabase()
    database.entries = [entries[key] for key in sorted(cited)]
    for entry in database.entries:
        if "OpenAI" in entry.get("author", "") and "note" in entry:
            # Immutable URLs and evidence ledgers already carry source provenance.
            entry["note"] = re.sub(
                r";?\s*(?:repository\s+)?snapshot\s+[0-9a-f]{40}(?:[;,]\s*accessed[^;]*)?",
                "", entry["note"], flags=re.I).strip(" ;,")
            if not entry["note"]:
                del entry["note"]
    writer = BibTexWriter()
    writer.order_entries_by = ("ID",)
    rendered = bibtexparser.dumps(database, writer)
    target = PAPER / "references.bib"
    if not target.exists() or target.read_text(encoding="utf-8") != rendered:
        target.write_text(rendered, encoding="utf-8", newline="\n")
    record = {"reference_count": len(cited), "all_references_cited": True,
              "missing": [], "unused_research_entries": sorted(entries.keys() - cited),
              "bibliographies": [str(p.relative_to(PAPER)) for p in paths]}
    scholarly = [key for key in cited if entries[key].get("ENTRYTYPE") in
                 {"article", "book", "inproceedings", "incollection"}
                 and "OpenAI" not in entries[key].get("author", "")]
    record["non_release_published_scholarly_references"] = len(scholarly)
    (PAPER / "audit").mkdir(exist_ok=True)
    (PAPER / "audit/citation-coverage.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
