# Lab

This is where new AI/data projects get built, before (or instead of) shipping them
anywhere public. Separate from the personal site — nothing in here is deployed by
GitHub Pages.

## Convention

Each project gets its own subfolder:

```
lab/
├── README.md            ← this file
└── <project-name>/
    ├── README.md         ← what it is, how to run it
    └── ...                the project's own code
```

A project can be anything — a script, a notebook, a small app, an MCP server, an
agent. No fixed stack. Use whatever the project calls for, and note how to run it in
that project's own README.

## Workspace tooling

This repo's `.claude/skills/` directory has agent skills installed for building this
kind of work — see `.claude/skills/README.md` for what's there and where each came
from.
