"""Build the review with pdfLaTeX and BibTeX; reject unresolved references/layout overflow."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess

PAPER = Path(__file__).resolve().parents[1]


def main():
    for tool in ("pdflatex", "bibtex"):
        if not shutil.which(tool):
            raise SystemExit(f"Missing executable: {tool}")
    work = PAPER / "build"
    work.mkdir(exist_ok=True)
    latex = ["pdflatex", "-interaction=nonstopmode", "-halt-on-error",
             "-file-line-error", f"-output-directory={work.as_posix()}", "main.tex"]
    commands = [latex, ["bibtex", "build/main"], latex, latex, latex]
    for index, command in enumerate(commands, 1):
        result = subprocess.run(command, cwd=PAPER, capture_output=True, text=True,
                                encoding="utf-8", errors="replace")
        (work / f"pass-{index}.txt").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"Build failed on pass {index}:\n{result.stdout[-4000:]}")
    log = (work / "main.log").read_text(encoding="utf-8", errors="replace")
    issues = [line for line in log.splitlines() if
              "Overfull" in line or "undefined" in line or "multiply defined" in line]
    if issues:
        raise RuntimeError("Unresolved build issues:\n" + "\n".join(issues))
    target = PAPER / "openai-mathematical-frontiers.pdf"
    shutil.copyfile(work / "main.pdf", target)
    audit = {"passes": 5, "issues": issues,
             "pages": int(re.search(r"Output written on [\s\S]*?\((\d+) pages", log)[1]),
             "pdf": target.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest()}
    (PAPER / "audit").mkdir(exist_ok=True)
    (PAPER / "audit/build.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
