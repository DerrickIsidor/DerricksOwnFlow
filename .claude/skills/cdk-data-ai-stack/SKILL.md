---
name: cdk-data-ai-stack
description: Use when working in infra/ — writing or reviewing AWS CDK (Python) stacks/constructs, Lambda functions, or SQL/database infrastructure for Derrick's data & AI projects. Also use when deciding how a new lab/ project should get deployed to AWS, or when setting up AWS credentials/CDK bootstrap for this repo. This is a living, growing knowledge base specific to this repo's infra conventions — not general CDK docs.
---

# CDK Data & AI Stack

This skill is this repo's private, accumulating knowledge base for its AWS CDK
infrastructure — conventions, architecture decisions, and patterns specific to
`infra/`. It is meant to grow: every time a real decision gets made (a construct
pattern adopted, a tradeoff resolved, a gotcha hit during deploy), it gets appended to
the relevant reference file below, so the next session — human or agent — doesn't
re-derive it from scratch.

This is distinct from `mcp-builder` and `skill-creator` (general Anthropic skills for
MCP servers and Claude Code skills respectively) and from `openai-docs` (OpenAI API
docs) — those stay as-is. This one is specific to *this repo's* infra and is expected
to be edited directly as things are learned, the same way `skill-creator` would guide
building any other skill.

## When to load which reference

| Reference | Load when |
|---|---|
| `references/conventions.md` | Any time you're about to add/change a stack or construct — naming, file layout, where things go |
| `references/decisions.md` | Before making an architectural choice, to check whether it was already decided (and why); after making one, to append it |
| `references/lambda-patterns.md` | Writing or reviewing a Lambda function/construct |
| `references/sql-patterns.md` | Writing or reviewing database infrastructure, schema, or migrations |
| `references/s3-patterns.md` | Writing or reviewing an S3 bucket construct, S3 event triggers, or multi-tenant/per-client parameterization (e.g. Pipeline-in-a-Box) |
| `references/setup-checklist.md` | Getting from "code scaffolded" to "actually deployed" — CLI install, credentials, bootstrap, first deploy |

## How this skill grows

1. When you resolve an open question (see `decisions.md`'s "Open questions" section)
   or discover a new pattern worth reusing, add it to the relevant reference file
   immediately — don't leave it only in chat history.
2. Decisions are append-only with a date; don't silently rewrite past entries when a
   decision changes — add a new dated entry that supersedes it and say so, so the
   history of *why* stays intact.
3. If a change here is significant, have the `bungi` agent log it in
   `docs/bungi/CHANGELOG.md` too — this skill is the durable "how", Bungi's changelog
   is the dated "what happened".
4. If this skill starts covering something general enough to be useful outside this
   repo (not specific to Derrick's stack), that's a signal to spin it out as its own
   skill using `skill-creator` instead of growing it here.

## Ground rules

- Never invent AWS account IDs, ARNs, resource names, or costs — pull them from the
  actual CDK code/output, or mark them as placeholders (`<ACCOUNT_ID>`, etc.).
- No real AWS credentials or secrets belong in this repo, ever — not in code, not in
  these reference docs, not in examples. Use `.env.example` / Secrets Manager
  references only.
- `cdk deploy`, `cdk destroy`, and `cdk bootstrap` touch real, billed AWS resources.
  Always confirm with the user before running them — same bar as a `git push`.
