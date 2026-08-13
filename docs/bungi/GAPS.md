# Gaps

Live backlog, not a diary — maintained by the `bungi` agent. Status is one of
`open` / `investigating` / `resolved`. "Last verified" is the last date someone
(Bungi or otherwise) actually checked the current repo state, not just repeated an
earlier claim.

---

## Open

- **`website/` move is uncommitted and incomplete.** `index.html`,
  `derricks-own-flow.html`, `dj-flow.html`, `dataflow.html` were moved into
  `website/`, but `assets/` and `tools/` are still at repo root, and root `CLAUDE.md`'s
  file map still documents the old root-level layout. Untracked in git as of this
  entry. Internal links (`../assets/shared.js` etc.) haven't been checked against the
  new layout.
  *First logged: 2026-08-13. Last verified: 2026-08-13 (`git status`).*

- **Newsletter form (`website/index.html`) doesn't send email.** Submit button calls
  `handleNL()` (local JS, browser-only confirmation) — not wired to Formspree or any
  backend. Fix instructions already exist in `CLAUDE.md` under "Making Forms Work".
  *First logged: 2026-06-04 (prior session). Last verified: 2026-08-13 (grepped
  `website/index.html`, confirmed `onclick="handleNL()"` still in place).*

- **LinkedIn/GitHub footer links in `website/dataflow.html` are bare placeholder
  URLs** (`https://linkedin.com`, `https://github.com`, no actual handle).
  *First logged: 2026-06-04. Last verified: 2026-08-13
  (`website/dataflow.html:417-418`).*

## Open — not re-verified this session (carried from 2026-06-04 audit)

These were true as of 2026-06-04 per prior project notes. Not rechecked against
current code in this pass — verify before treating as current fact.

- DJ booking form and DataFlow contact form likely have the same "browser
  confirmation only, no real email" issue as the newsletter form.
- DataFlow project cards are placeholders (`#` links, placeholder case studies).
- `derricks-own-flow.html` progression log has only placeholder "coming soon" cards.
- DJ Instagram footer link is a placeholder, not a real profile.
- DJ Flow mixes have play buttons with no actual audio linked.

## Resolved

*(none yet)*
