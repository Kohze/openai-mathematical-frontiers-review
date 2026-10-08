# Mathematical Frontiers in the OpenAI Research Release

**Cancellation, Positivity, and Changes of Representation**  
Robin Gounder · Vaionex Corporation · Manuscript dated 7 October 2026

[Read the review](openai-mathematical-frontiers.pdf) · [Citation metadata](CITATION.cff) · [Final audit](audit/final-audit.json)

This repository contains a comparative narrative review, its LaTeX sources,
reference and source-evidence ledgers, and reproduction scripts. The review
examines eight grouped case studies across arithmetic, convex and operator
inequalities, counting and sampling, computational hardness, group algebras,
and kinetic equations. It compares the conclusions claimed by the release
manuscripts with earlier literature and identifies the estimates, quantifiers,
and representation changes intended to support those conclusions.

The retained final audit records **25 pages, 83 cited references, and 43
published scholarly references outside the release**. The contribution is
comparative synthesis and explanatory examples. Claims from the underlying
release remain attributed to their source manuscripts.

## Evidence and scope

The package checks bibliographic identities, source-statement comparisons,
elementary illustrative examples, document compilation, and internal exposition
review. The saved visual-review record concerns the retained PDF. These checks
do **not** independently establish the underlying release theorems: their proofs
and formal dependency builds are outside this review's verification scope.
Internal reviews are recorded separately from external peer review.

The reviewed release records are pinned to
[`openai/math@adc7f1241b42e322a6451854ab7e4b4c146bf78a`](https://github.com/openai/math/tree/adc7f1241b42e322a6451854ab7e4b4c146bf78a).
Source locations and primary-literature records appear in the research ledgers.
This pin identifies the reviewed material; it does not imply a proof-build result.

Useful entry points:

| File or directory | Contents |
| --- | --- |
| [main.tex](main.tex), [overview.tex](overview.tex), [synthesis.tex](synthesis.tex) | Main manuscript and comparative synthesis |
| `research/*/section.tex` | Domain case-study sections |
| [references.bib](references.bib) | Assembled cited bibliography |
| `research/*/evidence.json`, [root evidence](research/root-evidence.json) | Source locators and primary-reference support |
| [Comparison register](research/comparison-register.json) | Case selection and transfer profiles |
| [Verification worksheet](research/verification-worksheet.json) | Source hypotheses and quantitative targets for further assessment |
| [Contrastive tests](research/contrastive-tests.tex) | Elementary tests of stronger transfer inferences |
| [Final audit](audit/final-audit.json), [review resolutions](audit/review-resolution.json) | Scope, checks, and dispositions of internal findings |
| [Illustrative example results](audit/illustrative-examples.json) | Exact finite and algebraic checks |
| [Artifact manifest](audit/artifact-manifest.json) | Hashes for the curated package |
| [reproduce/](reproduce/) | Bibliography, example, build, and packaging scripts |

## Reproduce from the repository root

Use Python 3.11 or later. A virtual environment is recommended; install the
tested Python dependencies with:

```sh
python -m pip install -r requirements.txt
```

The bibliography and elementary checks do not require TeX or a network lookup:

```sh
python reproduce/assemble_references.py
python reproduce/check_examples.py
```

To rebuild the PDF, install pdfLaTeX and BibTeX with the packages listed in
`main.tex`, then run:

```sh
python reproduce/build.py
```

For example, Ubuntu's `texlive-latex-base`, `texlive-latex-recommended`,
`texlive-latex-extra`, `texlive-fonts-recommended`, and `lmodern` packages supply
the workflow's TeX environment. The build writes intermediates to `build/`,
updates `openai-mathematical-frontiers.pdf`, and records its result in
`audit/build.json`. A fresh build may have different PDF bytes from the retained
PDF, even when its mathematical text is unchanged.

The packaging script checks the **retained** PDF against its saved build and
visual-review records, as well as bibliography coverage, evidence ledgers,
illustrative examples, and review resolutions:

```sh
python reproduce/package_review.py
```

Run that check before rebuilding if you want to validate the retained package.
After manuscript or PDF changes, its source-hash and visual-review assertions
require refreshed review records; rebuilding alone does not provide a new visual
review. In a standalone checkout the script writes generated packages under
`output/`. All scripts locate the manuscript relative to their own file paths,
so the commands above work from the repository root.

An optional network check of DOI bibliographic identities is:

```sh
python reproduce/verify_reference_metadata.py
```

That command refreshes `audit/reference-metadata.json` and can report lookup
failures or records needing human comparison. It does not establish source
theorem validity and is not a required network dependency of CI.

The GitHub workflow checks the retained package and the exact illustrative
examples on Linux and Windows. A separate Linux job rebuilds the LaTeX document
and uploads its PDF and build logs. Neither job executes the release proofs.
The `.gitattributes` file preserves line endings because the audit records hash
exact file bytes.

## Citation and rights

Please cite the manuscript using [CITATION.cff](CITATION.cff), and include the
repository commit or tag you used when referring to its supporting code or
evidence. 

Copyright Robin Gounder. Original reproduction scripts and illustrative checks are MIT licensed
under LICENSE-CODE. Manuscript reuse terms remain separate; a manuscript
reuse license has not been selected. Referenced third-party works remain subject to their respective terms.

The manuscript includes its generative AI disclosure in a dedicated section.
This repository provides the review and its supporting materials; it does not
represent acceptance or endorsement by a journal or by the reviewed release's
authors.
