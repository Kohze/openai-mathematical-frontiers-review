Mathematical Frontiers in the OpenAI Research Release
Cancellation, Positivity, and Changes of Representation

Robin Gounder, Vaionex Corporation, robin@gounder.com
7 October 2026

This is a separate comparative narrative review. Its contribution is the
literature synthesis, comparison of proof mechanisms and hypotheses, and
identification of the interfaces carrying the proposed mathematical advances.
Elementary worked examples explain those interfaces. Mathematical conclusions
of the release remain attributed to their source manuscripts.

FILES
main.tex and synthesis.tex: review sources.
research/*/section.tex: domain case-study sections.
references.bib: complete cited bibliography, assembled from verified research.
openai-mathematical-frontiers.pdf: compiled review.
research/*/evidence.json: supporting locations and primary reference records.
audit/: reference checks, build record, example checks and critical review.
audit/review-resolution.json: final disposition of internal review findings.
audit/final-audit.json: checks on the delivered manuscript and evidence package.
audit/artifact-manifest.json: file hashes for the curated paper package.
research/comparison-register.json: case selection and explicit transfer profiles.
research/verification-worksheet.json: exact geometry/operator hypotheses and
  quantitative source targets for further proof assessment.
research/round-2-evidence.json: six added closest-prior source records.
research/contrastive-tests.tex: elementary tests of stronger transfer inferences.

BUILD
Python needs bibtexparser and pypdf. A TeX installation needs pdfLaTeX, BibTeX and the
packages listed in main.tex.
  python reproduce/assemble_references.py
  python reproduce/check_examples.py
  python reproduce/build.py
  python reproduce/package_review.py

An optional network DOI metadata check is:
  python reproduce/verify_reference_metadata.py
This checks bibliographic identities. Source support is recorded separately
in the research ledgers. Neither metadata checking nor elementary-example
checking establishes a claimed source theorem.

The review contains 25 pages, eight grouped case studies and 83 cited references,
including 43 published scholarly works outside the release. Its novelty
assessment separates proposed conclusions, proof mechanisms and quantifiers.
The elementary examples serve exposition; the paper's contribution is the
comparative synthesis. Internal cross-review is recorded separately from
external peer review. The revised table separates the qualitative barrier,
inherited machinery and proposed new bridge. Earlier arithmetic cutoffs,
classical operator similarity and preceding scalar boundary-certificate
approaches are included in the closest-prior comparison.

SOURCE PROVENANCE
The review links individual release records to commit
adc7f1241b42e322a6451854ab7e4b4c146bf78a (6 October 2026).
This identifier supports reproducibility; it is not an additional mathematical
hypothesis. Source evidence and comparator correspondence are distinguished
from an independent formal verification execution in the research ledgers.

The earlier counting review and numerical-range paper remain in their own
folders. Public source repository: https://github.com/Kohze/openai-mathematical-frontiers-review.
Copyright Robin Gounder. Manuscript reuse license has not been selected.
