# Git Fundamentals — Quick Reference

Git tracks the history of your project. Every saved snapshot is called a **commit**.
You always work inside a **branch** — a parallel version of the code that you can later
merge back into the main version.

---

## The Three-Stage Flow

```
Working Directory  →  Staging Area  →  Repository (commit)
  (files on disk)     (what you're       (saved snapshot)
                        about to save)
```

1. You edit files on disk
2. You `add` the ones you want to save
3. You `commit` to create a permanent snapshot

---

## Daily Commands

### Check what's changed
```bash
git status
```
Shows: modified files (red = unstaged, green = staged), untracked new files.

```bash
git diff
```
Shows the exact line-by-line changes in unstaged files.

---

### Stage files (pick what goes into the next commit)
```bash
git add filename.html          # stage one file
git add assets/                # stage a whole folder
git add .                      # stage everything changed
```

---

### Commit (save a snapshot)
```bash
git commit -m "Your message here"
```
Write the message in plain English. Describe WHY you changed it, not what.
- Good: `"Add DJ booking form with Formspree"`
- Bad: `"updated stuff"`

---

### Push (send your commits to GitHub)
```bash
git push
```
This publishes your commits to GitHub Pages — the site goes live within ~60 seconds.

If it's your first push on a new branch:
```bash
git push -u origin your-branch-name
```

---

## Branches

A branch is a safe copy of the code to experiment in. Main is always the live site.
You work in a branch, and when you're happy, you merge it into main.

```
main  ──●──●──●──────────────●   (live site)
              \              /
    dev        ●──●──●──●──     (your working branch)
```

### Create and switch to a new branch
```bash
git checkout -b branch-name
```

### Switch between branches
```bash
git checkout main        # go to main
git checkout dev         # go back to dev
```

### See all branches
```bash
git branch               # local branches
git branch -a            # all branches including remote
```

---

## Merging (bringing work back to main)

When your feature is ready:

```bash
git checkout main          # 1. switch to main
git merge dev              # 2. bring dev's changes into main
git push                   # 3. push the updated main live
```

---

## Syncing with GitHub

### Pull latest changes (if you edited on GitHub.com or another machine)
```bash
git pull
```
Always pull before you start working if you've made changes elsewhere.

---

## The Full Workflow for This Site

```bash
# 1. Make sure you're on your working branch
git checkout dev

# 2. Edit files in VS Code / your editor

# 3. Check what changed
git status

# 4. Stage what you want to save
git add .

# 5. Commit with a clear message
git commit -m "Add new progression cards for week 3"

# 6. Push to GitHub
git push

# 7. When ready to go live — merge to main
git checkout main
git merge dev
git push
git checkout dev    # go back to keep working
```

---

## Undo & Fix Mistakes

| Situation | Command |
|-----------|---------|
| Unstage a file you added by accident | `git restore --staged filename` |
| Discard changes to a file (go back to last commit) | `git restore filename` |
| See the history of commits | `git log --oneline` |
| Undo the last commit (keep the changes) | `git reset --soft HEAD~1` |

> **Rule of thumb:** `git restore` undoes edits. `git reset` undoes commits.
> Both are safe as long as you haven't pushed yet.

---

## Glossary

| Term | What it means |
|------|---------------|
| **Repository (repo)** | Your project folder tracked by git |
| **Commit** | A saved snapshot of your files at a point in time |
| **Branch** | A parallel version of the code |
| **main** | The primary branch — what's live on derricksownflow.com |
| **origin** | Shorthand for your GitHub remote (the cloud copy) |
| **Staging area** | The list of changes queued for the next commit |
| **Push** | Send local commits up to GitHub |
| **Pull** | Bring GitHub's commits down to your machine |
| **Merge** | Combine one branch's history into another |
| **HEAD** | Pointer to your current position in history |
