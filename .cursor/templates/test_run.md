LLM Run Plan • Checklist • Summary

# Template Usage Rule

For every run or iteration:

- Use the external template at `.cursor/templates/test_run.md`.
- Before making changes: copy the **PLAN** block, fill it, and include it in your iteration log.
- During execution: update the **CHECKLIST** block to track progress, checking off items as they are completed.
- After execution: revise the **SUMMARY** block for the current iteration with results and follow‑ups.
- Keep only one living copy in `.cursor/run_logs/<branch>-run.md`, appending new iteration blocks as work progresses.
- Do not create new template files for each run; always base updates on the template and revise the living run log.