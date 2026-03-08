# COMMANDS.md — FDA Drug Label Project
# Updated: 2026Mar03-0859
# Parser version: 4.0.0

---

## Repository Setup

### Clone the repository
```bash
git clone https://github.com/[your-username]/[repo-name].git
cd [repo-name]
```

### Pull latest changes from branch
```bash
git pull origin claude/module-2-claude-instructions-6a9Sv
```

---

## Understanding "X commits behind main"

When a PR is merged, GitHub creates a **merge commit** on `main`. Your working
branch doesn't automatically receive that commit, so GitHub counts it as "behind"
— even if all your code is already in `main`. This is cosmetic, not dangerous,
but it can be confusing.

### Step 1 — Check whether "behind" actually matters

This shows what files differ between your branch and `main`. If your code is
already merged, the diff will be empty or only show unrelated changes.

```bash
git fetch origin main
git diff HEAD origin/main --stat
```

If the output is blank (or only shows files from other people's work), you are
not missing anything. The "behind" count is just merge bookkeeping.

### Step 2 — Fix it (make the branch show as up to date)

Merge the commits from `main` back into your branch. Because your code is
already there, this will never overwrite your work — it only pulls in the merge
bookkeeping commits.

```bash
git fetch origin main
git merge origin/main
git push origin [your-branch-name]
```

After this, GitHub will show "0 behind."

### Make this a habit

After any PR from this branch is merged into `main`, run the two commands above
to resync. Think of it as: *you sent your work up, now pull the receipt back
down.*

### Check branch and status
```bash
git status
git branch
```

### Create and switch to a working branch
```bash
git checkout -b [branch-name]
```

### Stage all changes and commit
```bash
git add -A
git commit -m "your message here"
```

### Push branch to GitHub
```bash
git push origin [branch-name]
```

### View recent commit history (last 20)
```bash
git log --oneline -20
```

### Undo the last commit (keeps file changes locally)
```bash
git reset --soft HEAD~1
```

### Discard all uncommitted changes (destructive — cannot be undone)
```bash
git checkout -- .
```

---

## Environment Setup

### Create a virtual environment
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows Command Prompt
python -m venv venv
venv\Scripts\activate.bat

# Windows PowerShell
py -m venv venv
venv\Scripts\Activate.ps1
```

### Install all dependencies
```bash
pip install -r requirements.txt
```

### Install a single package
```bash
pip install [package-name]
```

---

## Module 2 — Study Parser (v4.0.0)

All commands assume you are in the repository root with the virtual environment active.

---

### Step 1 — Run the full batch parser

Runs the parser over every `.txt` file in `labels_s14_txt/` and writes two output files:
- `batch_test_results_v3_m2t.json` — extracted study data (one entry per drug)
- `parse_diagnostics_YYYYMMDD.json` — per-drug diagnostic records

```bash
python3 M2_batch_runner_v1_0_0.py
```

#### With custom output paths
```bash
python3 M2_batch_runner_v1_0_0.py \
  --results-out batch_test_results_v4.json \
  --diag-out parse_diagnostics_v4.json
```

#### With debug logging (shows per-strategy match detail)
```bash
python3 M2_batch_runner_v1_0_0.py --verbose
```

---

### Step 2 — Validate extracted fields against label text

Reads the file named in `parser_config.json → batch_results_file`, checks each
study's extracted fields against the raw label text, and writes one JSON object
per study to stdout.

```bash
python3 validate_extractions_v1.py > VALIDATION_REPORT.jsonl
```

The summary (total / all-correct / mismatch / field-absent counts) is printed to stderr
and is visible in the terminal even when stdout is redirected.

---

### Step 3 — Build the study coverage map

Enumerates all study references in the label text, matches them against extracted
results, and classifies each as EXTRACTED / PARTIAL / MISSED / PHANTOM.
Writes `study_coverage_map.json`.

```bash
python3 map_study_coverage_v1.py
```

---

### Run the parser on a single label file

Useful for debugging a specific drug without running the full batch.

```bash
python3 M2_study_parser_v3_0_0.py \
  labels_s14_txt/aripiprazole_label_section14_p49-62.txt \
  aripiprazole
```

Replace `aripiprazole` with any drug name and point to its label file.
Output is printed to stdout (one study per line).

---

### Run unit tests

```bash
python3 -m unittest test_m2_parser -v
```

All 24 tests should pass. Run this after any change to the parser to check for
regressions before running the full batch.

---

### Inspect batch diagnostics for a specific drug

```bash
python3 -c "
import json
d = json.load(open('parse_diagnostics_20260303.json'))
import sys
drug = sys.argv[1]
print(json.dumps(d.get(drug, 'NOT FOUND'), indent=2))
" aripiprazole
```

Replace `aripiprazole` with the drug name and update the filename to match the
diagnostic file generated by your batch run.

---

### Check whether a label file has extractable text

```bash
python3 -c "
import sys
t = open(sys.argv[1]).read()
print(len(t.strip()), 'chars,', t.count('\n'), 'lines')
" labels_s14_txt/aripiprazole_label_section14_p49-62.txt
```

A result below ~200 chars indicates a failed PDF extraction.

---

### Change the active batch results file

Updates `batch_results_file` in `parser_config.json` so all three pipeline scripts
(batch runner, validate, map) point to the new filename without any code edits.

```bash
python3 -c "
import json
p = 'parser_config.json'
c = json.load(open(p))
c['batch_results_file'] = 'batch_test_results_v4.json'
with open(p, 'w') as f:
    json.dump(c, f, indent=2)
print('batch_results_file ->', c['batch_results_file'])
"
```

Replace `batch_test_results_v4.json` with whatever filename you need.

#### Read the current value without editing

```bash
python3 -c "import json; print(json.load(open('parser_config.json'))['batch_results_file'])"
```

---

### Check which exclusion keywords appear in a label

```bash
python3 -c "
import re, json, sys
kws = json.load(open('parser_config.json'))['exclusion_keywords']
t = open(sys.argv[1]).read()
for k in kws:
    m = re.search(k, t, re.I)
    if m:
        print(repr(k), 'at char', m.start())
" labels_s14_txt/ziprasidone_label_section14_p31-38.txt
```

---

## Module 2 — Output Files Reference

| File | Written by | Contents |
|------|-----------|----------|
| `batch_test_results_v3_m2t.json` | `M2_batch_runner_v1_0_0.py` | Extracted studies + parse_status per drug |
| `parse_diagnostics_YYYYMMDD.json` | `M2_batch_runner_v1_0_0.py` | ParseDiagnostic records per drug |
| `VALIDATION_REPORT.jsonl` | `validate_extractions_v1.py` | Field-level validation per study |
| `study_coverage_map.json` | `map_study_coverage_v1.py` | EXTRACTED/PARTIAL/MISSED/PHANTOM per study |
| `parser_config.json` | (static — edit manually) | exclusion_keywords, data_absent_drugs, max_acute_weeks, batch_results_file |

---

## Typical end-to-end run (copy-paste sequence)

```bash
# 1. Run the batch parser
py M2_batch_runner_v1_0_0.py

# 2. Validate extracted fields
py validate_extractions_v1.py > VALIDATION_REPORT.jsonl

# 3. Build coverage map
py map_study_coverage_v1.py

# 4. Run unit tests
py -m unittest test_m2_parser -v
```

---

## Module 1 — Step 3: Fetch FDA Approval Dates (M1S3)

Fetches the original NDA approval date for each compound from the FDA Drugs@FDA API.
Reads NDA numbers from `labels/nda_brand_cache.json` (produced by M1S1 — no other
prerequisite).

### Run (all compounds in cache)

```bash
# Windows
py M1S3_approval_dates.py

# macOS/Linux
python3 M1S3_approval_dates.py
```

### Specific compounds only

```bash
py M1S3_approval_dates.py --compounds aripiprazole quetiapine risperidone
```

### With FDA API key (higher rate limit: 240 vs 40 req/min)

```bash
py M1S3_approval_dates.py --api-key YOUR_OPENFDA_KEY
```

Free key at: https://open.fda.gov/apis/authentication/

### Force re-fetch (bypass skip logic)

```bash
py M1S3_approval_dates.py --force
```

### Verbose output

```bash
py M1S3_approval_dates.py --verbose
```

### Output files

| File | Description |
|------|-------------|
| `approval_dates.json` | Structured JSON keyed by compound — includes `original_approval_date`, `nda`, `brand_names`, `supplement_count`, `sponsor_name` |
| `APPROVAL_DATES.md` | Markdown table sorted by approval date; ready for report copy-paste or Claude context upload |

### Inspect results

```bash
# Print one compound's entry
python3 -c "
import json, sys
d = json.load(open('approval_dates.json'))
print(json.dumps(d.get(sys.argv[1], 'NOT FOUND'), indent=2))
" aripiprazole
```

```bash
# List all OK entries sorted by date
python3 -c "
import json
d = json.load(open('approval_dates.json'))
rows = [(v['original_approval_date'], k) for k, v in d.items() if v['status']=='OK']
for date, name in sorted(rows):
    print(date, name)
"
```

---

## Module 3 — Study Linker

### Configuration
Edit `parser_config_m3.json` to set:
- `ncbi_email` and `unpaywall_email` (required by API Terms of Service)
- `ncbi_api_key` (optional; raises PubMed rate limit from 3→10 req/s)
- `elsevier_api_key` (optional; covers ScienceDirect/Lancet/Cell Press — get key at dev.elsevier.com)
- `institutional_proxy_url` (optional; EZproxy prefix, e.g. `https://ezproxy.lib.myuniversity.edu/login?url=`)
- `scholar_enabled: true` to activate Google Scholar fallback (requires `pip install scholarly`)

Credentials can also be supplied as environment variables:

| Config key | Environment variable |
|---|---|
| `ncbi_api_key` | `NCBI_API_KEY` |
| `elsevier_api_key` | `ELSEVIER_API_KEY` |
| `institutional_proxy_url` | `EZPROXY_URL` |

### Commands

```bash
# Run the full linker (all compounds)
py M3_study_linker.py

# Run on specific compounds only
py M3_study_linker.py --compounds amisulpride aripiprazole

# Dry run — builds queries without making network calls
py M3_study_linker.py --dry-run

# Custom input / output files
py M3_study_linker.py --input batch_test_results_v5.json --output study_links_v1.json

# Run with browser login for OpenAthens / institutional access
# Opens browser, you log in to Tufts, hospital portal, etc., then press Enter
py M3_study_linker.py --browser-login

# Specify a browser other than Chrome (chrome | firefox | edge | safari)
py M3_study_linker.py --browser-login --browser firefox

# Browser login requires: py -m pip install browser-cookie3

# Generate coverage report (reads study_links_v1.json)
py M3_link_reporter.py

# Run unit tests
py -m unittest test_m3_linker -v
```

### Output files

| File | Description |
|---|---|
| `study_links_v1.json` | Full link records (CT record, PubMed matches, PDF paths, phase, zotero_verified) |
| `link_coverage_map.json` | Per-compound LINKED_PDF / LINKED_ABSTRACT / LINKED_CT_ONLY / NOT_FOUND counts |
| `LINK_REPORT.md` | Human-readable coverage report with per-study detail; `[Zotero verified]` annotations |
| `studies/<compound>/` | Phase 3/4 PDFs: `<Author> et al (<Year>) - <Study ID>.pdf` |
| `studies/Phase 1/<compound>/` | Phase 1 PDFs (detected via CT phases field or PubMed publication type) |
| `studies/Phase 2/<compound>/` | Phase 2 PDFs |

---

## Utilities

### UTIL_rollback_files — Separate outputs from a previous run

Copies (or moves) files older than a cutoff time from a source directory to a
destination directory.  Use this when outputs from two pipeline runs got mixed together.

The cutoff can be a datetime string or the modification time of any reference file
(run log, JSON output, etc.).  Always do a `--dry-run` first.

**PowerShell (Windows) — put all args on one line:**
```powershell
# Dry run using a reference file's timestamp as cutoff
py UTIL_rollback_files.py studies/ old_studies/ --since-file M3_first_run_2026Mar05-2324.txt --ext .pdf --dry-run

# With explicit datetime
py UTIL_rollback_files.py studies/ old_studies/ --since "2026-03-05 23:24:00" --ext .pdf --dry-run

# When the dry run looks right, move the files
py UTIL_rollback_files.py studies/ old_studies/ --since-file M3_first_run_2026Mar05-2324.txt --move
```

**macOS / Linux (bash):**
```bash
python3 UTIL_rollback_files.py studies/ old_studies/ \
    --since-file M3_first_run_2026Mar05-2324.txt --ext .pdf --dry-run

python3 UTIL_rollback_files.py studies/ old_studies/ \
    --since-file M3_first_run_2026Mar05-2324.txt --move
```

**Options:**

| Flag | Description |
|------|-------------|
| `--since "YYYY-MM-DD HH:MM:SS"` | Explicit cutoff datetime |
| `--since-file PATH` | Use mtime of this file as cutoff |
| `--move` | Move instead of copy (removes files from source) |
| `--ext .pdf .json` | Limit to specific extensions (default: all) |
| `--dry-run` | Print what would be transferred without touching files |

---

### Full pipeline M1 → M2 → M3

```bash
py M1_pipeline_orchestrator.py          # M1S1 + M1S2a + M1S2b
py M1S3_approval_dates.py               # approval dates (can run any time after M1S1)
py M2_batch_runner_v1_0_0.py
py M3_study_linker.py
py M3_link_reporter.py
```
