# Repository instructions

- Treat `docs/IMPLEMENTATION_PLAN.md` as the scope and release-gate authority.
- Implement one phase at a time and keep changes small and reviewable.
- Run the phase gate before creating a local commit.
- Never mark unavailable graphical checks as passed; record them as pending.
- Preserve user-local installation and never apply a theme automatically.
- Do not use symlinks inside Plasma packages.
- Never copy artwork from another theme. Existing themes may only be inspected
  to verify technical contracts.
- Do not implement deferred scope, push, tag, publish, or change remote services
  without explicit approval.
- Use English for code, comments, documentation, filenames, and commits.
