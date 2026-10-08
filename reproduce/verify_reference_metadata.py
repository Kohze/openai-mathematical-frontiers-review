"""Cross-check DOI metadata; retain failures for human inspection, never infer proof validity."""
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
from pathlib import Path
import html
import json
import re
import unicodedata
import urllib.parse
import urllib.request
import bibtexparser

PAPER = Path(__file__).resolve().parents[1]


def normalize(value):
    value = html.unescape(value)
    value = re.sub(r"\\(?:[A-Za-z]+|[^A-Za-z])", "", value)
    value = unicodedata.normalize("NFKD", value).lower()
    return re.sub(r"[^a-z0-9]", "", value)


def verify(entry):
    record = {"key": entry["ID"], "title": entry.get("title"), "year": entry.get("year"),
              "doi": entry.get("doi"), "primary_url": entry.get("url")}
    if not record["doi"]:
        record["metadata_status"] = "primary_record_in_research_ledger"
        return record
    url = "https://doi.org/" + urllib.parse.quote(record["doi"], safe="/")
    request = urllib.request.Request(url, headers={
        "User-Agent": "MathematicalFrontiersReview/1.0",
        "Accept": "application/vnd.citationstyles.csl+json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
        title_value = data.get("title", "")
        cross_title = title_value[0] if isinstance(title_value, list) else title_value
        score = SequenceMatcher(None, normalize(record["title"]), normalize(cross_title)).ratio()
        dates = {k: data[k].get("date-parts") for k in
                 ("published", "published-print", "published-online", "issued") if k in data}
        years = {str(parts[0][0]) for parts in dates.values() if parts and parts[0]}
        record.update({"crossref_title": cross_title, "title_similarity": round(score, 4),
                       "crossref_authors": data.get("author", []), "crossref_dates": dates,
                       "crossref_journal": data.get("container-title"),
                       "crossref_volume": data.get("volume"), "crossref_pages": data.get("page"),
                       "crossref_doi": data.get("DOI"),
                       "year_in_crossref_dates": record["year"] in years,
                       "metadata_status": "matched" if score >= .84 and record["year"] in years
                       else "manual_comparison_required"})
    except Exception as error:
        record.update({"metadata_status": "lookup_failed", "error": str(error)})
    return record


def main():
    entries = bibtexparser.loads((PAPER / "references.bib").read_text(encoding="utf-8")).entries
    with ThreadPoolExecutor(max_workers=2) as pool:
        records = list(pool.map(verify, entries))
    report = {"scope": "Bibliographic DOI identity, separate from claim support and proof validity",
              "accessed": "2026-10-07", "reference_count": len(records), "records": records}
    (PAPER / "audit/reference-metadata.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({status: sum(r["metadata_status"] == status for r in records)
                      for status in sorted({r["metadata_status"] for r in records})}, indent=2))
    for record in records:
        if record["metadata_status"] in {"manual_comparison_required", "lookup_failed"}:
            print(record["key"], record["metadata_status"], record.get("crossref_title", record.get("error")))


if __name__ == "__main__":
    main()
