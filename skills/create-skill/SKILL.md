---
name: create-skill
description: Turn a workflow the user already does themselves into a new skill, through a short Q&A rather than guessing at their process. Produces a SKILL.md sized to what the workflow actually needs, not an exhaustive checklist. Use only when explicitly invoked with $create-skill or /create-skill.
---

# Create skill

A skill worth keeping is someone's actual workflow, captured well enough that another agent reproduces the pattern without re-deriving it. Guessing at that workflow from a one-line description produces something generic. This workflow gets it from the user directly, in as few questions as it takes.

## Workflow

1. Ask for the skill's name and the general idea in one message. Do not proceed past this until both are given.
2. Ask what problem this solves, in the user's own words: what's painful about doing it without the skill. This is what the skill's description will state as its trigger.
3. Ask the user to walk through their own process, step by step, as if they were doing it themselves right now. This is the core of the skill. Follow up on any step that's vague ("then I check a few things") until it names something specific enough to write as an instruction.
4. Ask about scope and restrictions, only the ones relevant to what came out of step 3: read-only vs. allowed to write/push/publish, single project vs. general, language or tool restrictions, anything that must never happen.
5. Ask what the deliverable looks like: a summary, a decision, a file, code, a conversation. If the user says it depends, ask what it depends on rather than leaving it unresolved.
6. Ask how the skill should handle the situation where it doesn't have enough information to proceed. Silently assuming is rarely what the user wants. Confirm whether they'd rather it ask, flag and continue, or something else.
7. Create `~/projs/pouch/skills/<name>/SKILL.md` from the answers. Match the format of an existing skill. Keep only the steps that the user described.
8. Set the front matter `name` to the directory name. Use the description to state when the skill applies.
9. Read the completed skill. Check its steps against the user's answers. The shared symlink makes the skill available without an install step.

## Question discipline

Ask in small batches grouped by topic (problem, then workflow, then scope/output), not one long form. Stop asking once an answer is specific enough to write as an instruction. Do not chase detail the workflow doesn't need. If the user answers a later question while addressing an earlier one, don't re-ask it.

## Output

A new `~/projs/pouch/skills/<name>/SKILL.md` with a matching front matter name and a description that states when the skill applies.
Use imperative steps with clear inputs and outputs. Remove all placeholder text.
Include project details only when the skill applies to that project.

## Validation

- The front matter name matches the directory name.
- The shared skills link exposes the source file.
- Every workflow step in the finished file traces back to something the user actually said, not an assumption filled in during drafting.
