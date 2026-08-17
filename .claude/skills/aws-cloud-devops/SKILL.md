---
name: aws-cloud-devops
description: Use whenever the task touches AWS/cloud architecture in general, Docker or Kubernetes, Linux/shell administration, Git workflows, CI/CD, or security zone design — the "how do I run and operate this reliably" side of a project. Trigger on questions about which AWS service to use, containerizing an app, deployment pipelines, server/networking basics, or "how should this be hosted" even if the user doesn't say "DevOps" explicitly. For this repo's own AWS CDK infrastructure specifically (infra/), use cdk-data-ai-stack and the cdk-engineer agent instead — this skill is the general knowledge layer underneath that.
---

# AWS Cloud & DevOps

General cloud/DevOps knowledge — the layer underneath this repo's specific CDK stack.
When the work is actually touching `infra/`, hand off to `cdk-data-ai-stack` (this repo's
real conventions/decisions) and the `cdk-engineer` agent instead of re-deriving generic
advice here.

## Picking an AWS service — decide by shape of the workload, not familiarity

| Need | Reach for | Not this, unless... |
|---|---|---|
| Run code on a schedule/event, no server to manage | Lambda | ...it runs >15 min or needs a persistent connection — then a container/EC2 |
| Relational data, need SQL, low ops overhead | Aurora Serverless v2 (Postgres/MySQL) — what `infra/` uses | RDS classic if you need a specific extension Aurora lacks |
| Object storage (files, backups, data lake) | S3 | EFS only if you need a real POSIX filesystem shared across instances |
| Containerized app, need control over runtime | ECS Fargate (no server management) or EKS (if you already run Kubernetes elsewhere) | Raw EC2 unless you specifically need OS-level control |
| Message queue between services | SQS (simple queue) or Kafka/MSK (ordered streams, replay) | Don't reach for Kafka until you actually need replay/ordering — SQS is simpler and cheaper |

Cost and account details are never to be invented — pull real pricing from current AWS
docs (WebSearch/WebFetch) or the actual CDK output; never state a number from memory as
fact when it affects a real spending decision.

## Docker essentials

```bash
# The core lifecycle
docker build -t myimage:tag .          # build from a Dockerfile in cwd
docker run -d -p 8080:8080 --name app myimage:tag   # run detached, map a port
docker logs -f app                     # follow logs
docker exec -it app bash               # shell into a running container
docker ps -a                           # list containers (add -a for stopped ones too)
docker rm -f app                       # force stop + remove
```

Dockerfile shape — smallest reasonable image, most-stable-layer-first for cache reuse:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt   # deps layer — changes rarely
COPY . .                                              # code layer — changes often
CMD ["python", "app.py"]
```

Put things that change rarely (base image, dependency installs) *before* things that
change often (application code) — Docker caches each layer, so ordering this way means
a code-only change doesn't force a full dependency reinstall on every build.

**Kubernetes**, in one paragraph: it's a scheduler for containers across a cluster of
machines — it decides where each container runs, restarts it if it dies, and can scale
the number of replicas up/down. Reach for it only once you're running enough containers,
across enough machines, that manual placement/restart is genuinely a problem — for a
single service or a small handful of them, ECS Fargate or even a single Docker host is
simpler and cheaper to operate.

## Linux/shell basics worth having automatic

- `cron` for scheduled jobs (`crontab -e`), systemd for long-running services.
- Package management differs by distro (`apt` on Debian/Ubuntu, `yum`/`dnf` on
  RHEL/Amazon Linux) — check which base image/AMI is in play before assuming a command.
- Shell scripts should `set -euo pipefail` at the top (exit on error, exit on unset
  variable, fail a pipeline if any stage fails) — without this, a script can silently
  continue past a real failure.

## Git workflow

```bash
git checkout -b feature/thing     # branch before changing anything on a shared repo
git add -p                        # stage hunks selectively — review before you commit
git commit -m "concise, imperative summary"
git push -u origin feature/thing
```

Never rewrite history (`rebase -i`, `push --force`) on a branch others might have pulled,
and never commit secrets — if one lands in a commit, rotating the credential is the fix,
not just removing it from a later commit (it's still in history).

## Security zone design — the shape of "don't put everything in one network"

Separate tiers by trust level and put a boundary between them: public-facing (load
balancer/API gateway) → application tier → data tier (database), with each tier only
able to reach the one directly behind it, not skip ahead. In AWS terms this is public
subnets for anything internet-facing, private subnets for application and database
tiers, security groups scoped to "only this tier can talk to that tier on this port" —
not one flat network where everything can reach everything. This repo's actual VPC/subnet
layout lives in `infra/` — check `cdk-data-ai-stack` before assuming a generic layout
applies here.

## CI/CD, in brief

The point of a pipeline is that "deployed" always means "passed the same checks every
time," not "whatever was on someone's laptop." Minimum shape: on every push, run tests →
build → (for a reviewed/approved change) deploy. Keep deploy credentials out of the
pipeline config itself — use the CI system's secret store, never a hardcoded key.

## Where this hands off

- Actually writing/changing `infra/` (the CDK Python stack, Lambdas, VPC) → the
  **cdk-engineer** agent and **cdk-data-ai-stack** skill, not this one.
- The data/pipeline layer running *inside* that infra → **sql-data-engineering** skill.
