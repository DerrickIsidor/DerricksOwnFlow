# DerricksOwnFlow — Site Editing Guide

This is Derrick's personal website at **derricksownflow.com** (hosted on GitHub Pages).
Everything here is plain HTML/CSS/JS — no build tools, no frameworks, no installs required.
Open any `.html` file in a browser and it works.

---

## File Map

```
DerricksOwnFlow/
├── index.html               ← Main hub / portal (Derrick.)
├── derricks-own-flow.html   ← Wheelie & lifestyle world (ember/orange)
├── dj-flow.html             ← DJ world (acid green)
├── dataflow.html            ← Data & tech world (blue / light theme)
├── tools/
│   └── fire-calculator.html ← First free tool (FIRE Calculator)
├── assets/
│   └── shared.js            ← Cross-page nav bar — ONE file controls all pages
│                               Exports: initSharedNav(), initToolNav()
├── CNAME                    ← Domain: derricksownflow.com
└── CLAUDE.md                ← This file
```

---

## Tool Page Standard — REQUIRED on Every New Tool/Sub-Page

Every file inside `tools/` (or any new standalone page outside the root) **must** include both nav functions from `shared.js`. This is non-negotiable — it keeps all pages connected to the brand system.

### Boilerplate (copy for every new tool)

**End of `<body>`, before `</body>`:**
```html
<script src="../assets/shared.js"></script>
<script>
  initToolNav('Tool Section Label', { basePath: '../' });
  initSharedNav('data', { theme: 'dark_warm', basePath: '../' });
</script>
```

**What each call does:**
- `initToolNav(label, opts)` — injects a fixed dark nav bar at `top:40px` (below the world-nav) with `← Derrick` on the left and your label on the right. Always call this **before** `initSharedNav`.
- `initSharedNav(activeId, opts)` — injects the world-switcher bar at `top:0` (40px tall), which always floats above everything else.

**Nav stack on tool pages (top → bottom):**
```
top:0  → height:40px  → world-switcher bar (z-index:200)
top:40 → height:60px  → tool nav: ← Derrick / Label (z-index:150)
top:100 → page content starts
```
So the hero / first content area of any tool page needs **at least 100px top padding**.

**`basePath` rule:** always `'../'` for files one level deep (`tools/`), `'../../'` for two levels deep, etc.

**Do NOT add a `<nav>` element** in the HTML — `initToolNav` creates and injects it automatically.

---

## Colors (Brand System)

| Token | Hex | Used for |
|-------|-----|----------|
| `--ember` | `#EF7B2B` | Derrick's Own Flow, main accent |
| `--acid` | `#D4FF00` | DJ Flow accent |
| `--blue` | `#1A6BFF` | DataFlow accent |
| `--cream` | `#F2E8D9` | Primary text on dark pages |
| `--void` | `#0A0806` | Darkest background |

Each page declares its own CSS variables at the top of its `<style>` block. Change them there
to retheme that page.

---

## Shared Navigation Bar

The world-switcher bar (the small sticky bar showing all 4 worlds) lives in **`assets/shared.js`**.
It is the ONLY place you need to edit to:
- Change a nav label (e.g. "Own Flow" → "Flow World")
- Change nav link colors
- Add a 5th world

Each page calls it like this (near the bottom of the `<script>` block):
```js
initSharedNav('home');   // index.html
initSharedNav('flow');   // derricks-own-flow.html
initSharedNav('dj');     // dj-flow.html
initSharedNav('data');   // dataflow.html
```

---

## How to Edit Each Page

### index.html — The Hub

**Tagline / hero text** — Search for `hero-desc` and edit the paragraph:
```html
<p class="hero-desc">
  <strong>Wheelie creator. DJ. Data engineer.</strong> Three worlds...
</p>
```

**About section** — Search for `<section id="about">` and edit the paragraphs inside `.about-body`.

**Manifesto quotes** — Search for `manifesto-lines` and edit the `.manifesto-line` divs.

**Social links** — Search for `<section id="connect">` and update the `href` attributes on `.connect-card` elements:
```html
<a href="https://instagram.com/flow.derrick" ...>
<a href="https://youtube.com/@derricksownflow" ...>
```

**Newsletter** — Currently shows a browser confirmation only. To make it actually send emails,
see the [Making Forms Work](#making-forms-work) section below.

---

### derricks-own-flow.html — Lifestyle World

**Hero tagline** — Search for `hero-tagline` and edit the paragraph.

**Stats boxes** — Search for `about-stats` and edit the `.stat-num` / `.stat-label` divs.
The "days" counter auto-calculates from a hardcoded start date. To change the start date:
```js
const startDate = new Date('2025-01-01');  // ← change this
```

**Adding a progression card** — Find `<div class="progression-grid" id="prog-grid">` and add:
```html
<div class="prog-card" data-type="progress">   <!-- or "tutorial" or "mindset" -->
  <div class="prog-card-bg">07</div>           <!-- card number -->
  <div class="prog-placeholder">
    <div class="prog-plus">+</div>
    <span>Coming soon</span>
  </div>
  <div class="prog-card-inner">
    <div class="prog-date">Month Year</div>
    <div class="prog-title">CLIP TITLE HERE</div>
    <div class="prog-tag">Progress · Description</div>
  </div>
</div>
```
Set `data-type` to `progress`, `tutorial`, or `mindset` to make the filter tabs work.

To add a real video thumbnail background to a card, add this inside `.prog-card`:
```html
<img src="path/to/thumbnail.jpg" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0.6;">
```

**Mindset principles** — Search for `<div class="principles">` and add/edit `.principle` divs.

---

### dj-flow.html — DJ World

**Adding a set card** — Find `<div class="sets-grid">` and copy/paste a `set-card` block:
```html
<div class="set-card">
  <div class="set-card-bg">
    <div class="set-wave" id="wave7"></div>  <!-- increment the ID -->
  </div>
  <div class="set-overlay"></div>
  <div class="set-play"><svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg></div>
  <div class="set-info">
    <div class="set-genre">Genre · Sub-genre</div>
    <div class="set-name">SET NAME</div>
    <div class="set-meta">City · Year</div>
  </div>
</div>
```
Then in the `<script>`, add the new wave ID to the array:
```js
['wave1','wave2',...,'wave7'].forEach(...)
```

**Adding a mix to the list** — Find `<div class="mixes-list">` and add a `.mix-row`:
```html
<div class="mix-row">
  <span class="mix-num">06</span>
  <div class="mix-info">
    <div class="mix-title">Mix Title Here</div>
    <div class="mix-sub">Subgenre · Description</div>
  </div>
  <span class="mix-tag tag-house">House</span>  <!-- tag-house|tag-techno|tag-latin|tag-soca -->
  <span class="mix-duration">1h 00m</span>
  <div class="mix-play-btn"><svg viewBox="0 0 24 24"><polygon points="5,3 19,12 5,21"/></svg></div>
</div>
```

**Booking specs** (location, genres, status) — Search for `<div class="booking-specs">` and edit the `.spec-row` divs.

---

### dataflow.html — DataFlow

**Adding a project** — Find `<div class="projects-grid">` and copy a `.project-card`:
```html
<div class="project-card">
  <div class="project-header">
    <span class="project-num">05</span>
    <div class="project-tags">
      <span class="project-tag tag-eng">Engineering</span>  <!-- tag-eng|tag-sci|tag-viz|tag-ml -->
    </div>
  </div>
  <div class="project-title">Project Name</div>
  <p class="project-desc">One or two sentence description of what you built and the impact.</p>
  <div class="project-stack">
    <span class="stack-pill">Python</span>
    <span class="stack-pill">dbt</span>
  </div>
  <a href="#" class="project-link">View project</a>  <!-- replace # with real link -->
</div>
```

**Skills bar** — Search for `<div class="skills-bar">` and add/remove `.skill-item` entries.

**About quote** — Search for `about-quote` and edit the `<blockquote>` text.

**Skills chips** — Search for `<div class="skills-list">` and edit the `.skill-chip` divs.

---

## Making Forms Work

All three forms (newsletter, DJ booking, data contact) currently only show a browser message.
To make them actually send you an email:

### Option 1 — Formspree (free, recommended)
1. Go to [formspree.io](https://formspree.io) and create a free account
2. Create a new form — you'll get a URL like `https://formspree.io/f/xabcdefg`
3. On each form's submit button, replace the `onclick` handler with a real `<form>`:

**Newsletter example (index.html):**
```html
<!-- Replace the nl-form div with this: -->
<form class="nl-form" action="https://formspree.io/f/YOUR_ID" method="POST">
  <input class="nl-input" type="text" name="name" placeholder="Your name" required/>
  <input class="nl-input" type="email" name="email" placeholder="your@email.com" required/>
  <button class="nl-btn" type="submit">Join the journey →</button>
</form>
```

**Booking form (dj-flow.html):**
```html
<form class="booking-form" action="https://formspree.io/f/YOUR_ID" method="POST">
  <!-- keep all existing inputs/selects/textarea, just add name="" to each -->
  <!-- and change the button to type="submit" -->
</form>
```

### Option 2 — mailto (simplest, no account needed)
```html
<form action="mailto:your@email.com" method="POST" enctype="text/plain">
```
This opens the user's email client — works but looks less polished.

---

## Social Links Quick Reference

Update these across the files:

| Platform | Current handle | Files to update |
|----------|---------------|-----------------|
| Instagram | `flow.derrick` | index.html, derricks-own-flow.html |
| YouTube | `@derricksownflow` | index.html, derricks-own-flow.html |
| DJ Instagram | (placeholder) | dj-flow.html footer |
| LinkedIn | (placeholder `linkedin.com`) | dataflow.html footer |
| GitHub | (placeholder `github.com`) | dataflow.html footer |

---

## Deploying Changes

This site is on **GitHub Pages**. To publish changes:
```bash
git add .
git commit -m "Your description of what changed"
git push
```
Changes go live at derricksownflow.com within ~60 seconds.

---

## Adding a New World / Page

1. Create a new `.html` file (copy an existing one as a starting point)
2. Add an entry to the `WORLDS` array in `assets/shared.js`:
   ```js
   { id: 'myworld', label: 'My World', href: 'myworld.html', color: '#FF0000' },
   ```
3. Call `initSharedNav('myworld')` in the new page's script
4. Add the new page to the footer links on all other pages

---

## Lab & Agent Tooling

Beyond the public site, this repo is also Derrick's workspace for building, shipping,
and sharing AI/data projects:

- **`lab/`** — new projects live here, each in its own subfolder. Not deployed by
  GitHub Pages; see `lab/README.md`.
- **`.claude/skills/`** — Claude Code skills installed for this kind of work
  (skill-creator, mcp-builder, agentic-eval, prompt-engineer, openai-docs). See
  `.claude/skills/README.md` for what each does and where it came from.
- **`.mcp.json`** — registers the `openaiDeveloperDocs` MCP server the `openai-docs`
  skill depends on.
- **`bungi`** (`.claude/agents/bungi.md`) — a subagent that documents changes, tracks
  open gaps between the docs and the actual repo, and researches knowledge gaps using
  the skills above. Invoke it after finishing meaningful work ("have Bungi document
  this") or to audit the project ("ask Bungi what's out of date" / "find gaps"). It
  reads the whole repo but only writes to `docs/bungi/` (`CHANGELOG.md`, `GAPS.md`,
  `RESEARCH.md`) — never commits, never touches application code.

None of this affects the deployed site — the file map and editing instructions above
still apply to the public pages.

That's it — the nav bar updates everywhere automatically.
