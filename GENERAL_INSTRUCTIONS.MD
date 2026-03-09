Here are some general instructions for all sessions.


The copyable python commands that Claude generates are very helpful. There is a document called COMMANDS*.MD that lists copyable terminal commands to clone and pull a GitHub repo. Please generate stepwise commands to set up and run this program and replace the existing set of stepwise commands with it. Please add any other GIT commands you feel would be helpful for active programming with Claude Code/Claude Code for Web

TIMESTAMPS:
Please update project documents such as the Bug Fix Log and Module# Workflow whenever you make changes to the scripts/programs. Please mark these documents with a timestamp in a format like: YYYY(3-letter month)DD-TTTT, where the time is in EST (e.g. 2026Feb05-2146)




## Execution Efficiency

### File reading
- To inspect a known section of a large file, use grep to find the line
  number then sed -n 'N,Mp' to read only those lines. Do not cat files
  over 200 lines unless the full content is required.
- To confirm a file was written successfully, print the filename and
  character count only. Do not preview output files unless asked.

### Syntax validation
- After writing or modifying any Python file, run
  python3 -m py_compile <filename> before executing it.
- Test any new regex pattern in isolation with
  python3 -c "import re; re.compile(r'<pattern>')"
  before embedding it in source.

### Pipeline execution
- The M2 pipeline (M2_batch_runner → validate_extractions →
  map_study_coverage) produces stable output files committed to the repo.
  Do not re-run the pipeline unless a prompt explicitly modifies a parser
  or extractor .py file. If a prompt only reads output JSONs, use the
  existing files.
- When running pipeline scripts, suppress INFO-level log output with
  2>/dev/null unless the logs are needed for diagnosis.

### Output verbosity
- Do not print JSON objects or large data structures inline. Use slices:
  list(data.items())[:3] or data['key'] for targeted inspection.
- For batch/pipeline runs, print only the final summary line, not
  per-drug progress lines.

### Verification
- Consolidate verification: apply all edits for a prompt, then run a
  single verification pass, rather than verifying after each individual
  change.

### Session boundaries
- Each prompt that ends with a git commit is a natural session boundary.
  If context is running low, commit and note "continue in next session."
  Do not batch work from multiple prompts into a single commit.


### Project documentation
- Narrative Summary: narrative summary of the program, its components, and step-by-step instructions for running all components
- Bug Fix Log: create as placeholder for now, will fill with bug fixes
- COMMANDS.MD: update with copyable terminal commands to use the program. Please print them with py instead of python

### Timestamps 
Please update project documents such as the Bug Fix Log and Narrative Summary whenever you make changes to the scripts/programs. Please mark these documents with a timestamp in a format like: YYYY(3-letter month)DD-TTTT, where the time is in EST (e.g. 2026Feb05-2146)

Please update the version number in module script filenames when you generate them.

### File reading
- To inspect a known section of a large file, use grep to find the line
  number then sed -n 'N,Mp' to read only those lines. Do not cat files
  over 200 lines unless the full content is required.
- To confirm a file was written successfully, print the filename and
  character count only. Do not preview output files unless asked.

### Syntax validation
- After writing or modifying any Python file, run
  python3 -m py_compile <filename> before executing it.
- Test any new regex pattern in isolation with
  python3 -c "import re; re.compile(r'<pattern>')"
  before embedding it in source.

### Pipeline execution
- Do not re-run a pipeline unless a prompt explicitly modifies a parser
  or extractor .py file. If a prompt only reads output JSONs, use the
  existing files. For example, the M2 pipeline (M2_batch_runner → validate_extractions →
  map_study_coverage) produces stable output files committed to the repo.
- When running pipeline scripts, suppress INFO-level log output with
  2>/dev/null unless the logs are needed for diagnosis.

### Output verbosity
- Do not print JSON objects or large data structures inline. Use slices:
  list(data.items())[:3] or data['key'] for targeted inspection.
- For batch/pipeline runs, print only the final summary line, not
  per-drug progress lines.

### Verification
- Consolidate verification: apply all edits for a prompt, then run a
  single verification pass, rather than verifying after each individual
  change.


