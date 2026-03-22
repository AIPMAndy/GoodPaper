# GoodPaper

**Open-source paper formatting helper for `.docx` / `.docm` manuscripts.**

GoodPaper focuses on one practical problem:

> **given a target paper template, check whether a manuscript matches it, generate a first-pass formatting fix, and export structured reports for manual cleanup.**

It is **not** an AI writing tool.
It is a **paper formatting + compliance helper** for authors, labs, teaching staff, and editors.

---

## Why this project exists

In real paper submission workflows, the painful part is often not writing the content itself, but:

- aligning the manuscript with a required template
- checking whether headings / abstract / references are styled correctly
- batch-reviewing multiple student or lab submissions
- doing the **first formatting pass automatically** before human polish

GoodPaper is built for that exact workflow.

---

## What GoodPaper can do

- Check a manuscript against a target Word template
- Detect common paper structure and style mismatches
- Generate a first-pass formatted `.docx`
- Run **check → format → re-check** in one step
- Batch-check multiple papers and export reports
- Work through both **CLI** and **local Web UI**

---

## Current rule coverage

GoodPaper currently covers these common academic structure elements:

- title
- author
- affiliation / address
- abstract
- keywords
- heading level 1 / 2
- first paragraph after heading
- table caption
- figure caption
- displayed equation
- references heading and reference items

---

## Typical use cases

GoodPaper is useful when you want to:

- check a conference / journal submission before upload
- help students align papers to a required template
- batch-review a folder of manuscripts in a lab or course
- do the **first formatting pass automatically**, then finish the remaining edits manually

---

## Open-source mode

This repository is prepared as an **open-source usable version**.

That means:

- no mandatory activation by default
- no committed commercial secret
- no committed local runtime artifacts
- no bundled third-party template file by default

So people can clone the repo and run it directly.
If they want to format against a real publisher / conference template, they should **upload their own template file** or configure a local template package.

---

## Why the repo does not bundle publisher templates

Many publisher / conference templates (`.docm`, `.dotm`, etc.) may have redistribution restrictions.

To avoid copyright and redistribution risk, this open-source repo does **not** ship third-party templates publicly.

Recommended usage:

1. **upload your own template file** in Web UI or CLI
2. or define your own package under `template_packages/`

---

## Quick start

### 1) Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Start the Web UI

```bash
python3 app.py serve
```

Then open:

```bash
http://127.0.0.1:8765
```

### 3) Use your own template

In the open-source version, the safest path is:

- upload a `.docx` / `.docm` template
- upload a manuscript
- run check / format / batch report

---

## CLI examples

### List template packages

```bash
python3 app.py list-packages
```

If no valid built-in package is available, just pass `--template` directly.

### Check a paper

```bash
python3 app.py check \
  --paper path/to/paper.docx \
  --template path/to/template.docm
```

### Format a paper

```bash
python3 app.py format \
  --paper path/to/paper.docx \
  --output outputs/paper-formatted.docx \
  --template path/to/template.docm
```

### Check and format in one step

```bash
python3 app.py check-and-format \
  --paper path/to/paper.docx \
  --output outputs/paper-formatted.docx \
  --template path/to/template.docm
```

### Batch check a folder

```bash
python3 app.py batch-check \
  --input-dir path/to/folder \
  --output-dir outputs/batch-report \
  --template path/to/template.docm
```

---

## Web UI features

The local Web UI supports:

- runtime status / optional activation display
- selecting a template package if one exists
- overriding with an uploaded template file
- single-document check
- format-only download
- check-and-format download
- batch report ZIP download

---

## Output artifacts

GoodPaper can generate:

- formatted `.docx`
- structured issue list
- paragraph-level findings
- fix plan
- recommendations
- batch `summary.json`
- batch `documents.csv`
- batch `issues.csv`

---

## Template packages

If you want to define reusable template packages, the structure looks like this:

```text
template_packages/
  your_package/
    manifest.json
```

Example manifest:

```json
{
  "package_id": "your_template",
  "name": "Your Template",
  "description": "Your local template package.",
  "version": "0.1.0",
  "default": true,
  "template_file": "../../path/to/your-template.docm",
  "semantic_styles": {
    "title": "papertitle",
    "author": "author",
    "address": "address",
    "abstract": "abstract",
    "keywords": "keywords",
    "heading_1": "heading1",
    "heading_2": "heading2",
    "first_paragraph": "p1a",
    "table_caption": "tablecaption",
    "figure_caption": "figurecaption",
    "equation": "equation",
    "references": "referenceitem"
  }
}
```

---

## Code review summary

Before making this repo public, the project was reviewed and cleaned up for open-source readiness.

Main fixes already made:

- switched the repository license to **Apache-2.0**
- removed reliance on committed local activation state
- ignored local artifacts like `.goodpaper/`, `outputs/`, `.DS_Store`
- replaced vendor secret config with `vendor.example.json`
- made open-source mode usable without activation
- avoided hard dependency on bundled third-party template files
- improved README for public GitHub usage

Still recommended next:

- add tests
- add a sample safe template / demo manuscript pair
- add screenshots or GIFs for the Web UI
- add CI checks
- improve validation coverage beyond current semantic rules

---

## Project status

GoodPaper is already useful as a **local open-source tool**, but it is still early-stage software.

What is already good:

- clear scope
- runs locally
- CLI + Web UI both work
- useful for first-pass paper formatting workflows
- structured report output is practical

What still needs work:

- automated tests
- more robust DOCX / DOCM edge-case handling
- more publisher / conference template adapters
- better UI polish
- sample test papers
- clearer plugin-style template package system

---

## Optional private distribution mode

The repo still keeps optional activation-related code so it can support private deployment or commercial distribution later.

If you want to enable private activation flow:

- create `config/vendor.json`
- or set `GOODPAPER_VENDOR_SECRET`
- and run with `GOODPAPER_REQUIRE_ACTIVATION=1`

That mode is **not required** for the public open-source repo.

---

## License

Apache-2.0
