# Documentation Guidelines

## Purpose

This document defines how documentation is maintained throughout the project. The objective is to keep the documentation simple, consistent, and useful for understanding the project's evolution.

---

## Objectives

The documentation aims to:

* Explain what is being built.
* Explain why a particular design or implementation was chosen.
* Explain how the application is implemented.
* Record the evolution of the project.
* Help during debugging and future maintenance.
* Help future developers understand and extend the project.
* Preserve sufficient context for future LLM-assisted development.
* Assist in viva preparation by documenting the reasoning behind important decisions.

---

## Documentation Philosophy

Documentation is treated as a first-class artifact of the project, just like the source code.

It is intended to be an engineering notebook rather than merely project documentation. The focus is on preserving the engineering thought process in addition to the final implementation.

---

## Documentation Principles

The documentation should always be:

* Simple
* Neat
* Readable
* Consistent
* Easy to maintain

Whenever there is a choice between a sophisticated documentation style and a simpler one that communicates equally well, the simpler approach should be preferred.

---

## Format

Documentation is written entirely in Markdown (`.md`).

Formatting should be limited to:

* Headings
* Bullet lists
* Numbered lists
* Tables (only when they improve readability)
* Code blocks

Avoid unnecessary formatting or decorative elements.

---

## Documentation Structure

Most documentation files should follow this structure:

1. Purpose
2. Current State
3. Design Evolution

Additional sections may be added whenever required.

---

## Current State

The **Current State** section always describes the latest accepted design or implementation.

This section should always remain synchronized with the current codebase.

A reader should be able to understand the current project without reading the design history.

---

## Design Evolution

The **Design Evolution** section preserves the project's engineering history.

Whenever a design changes, the previous design should not be deleted.

Instead, a new entry should be added explaining:

* the decision,
* the reason,
* alternatives considered (if applicable),
* impact (if applicable),
* current status.

Each entry should include the date on which the decision was made.

Possible status values include:

* Current
* Superseded
* Rejected

---

## Development Log

`development-log.md` is maintained separately.

It records development progress chronologically.

Typical entries include:

* Completed work
* Problems encountered
* Decisions made
* Next steps

Entries are append-only.

---

## Documentation Workflow

Whenever a significant piece of work is completed:

1. Discuss and reason about the design.
2. Implement the feature.
3. Review the implementation.
4. Identify affected documentation.
5. Update the documentation.
6. Review the documentation for correctness.

Documentation should always follow implementation and reflect the implemented system.

---

## Responsibilities

### Developer

Responsible for:

* Requirements analysis
* Design decisions
* Implementation
* Code review
* Verifying documentation

### AI Assistant

Responsible for:

* Preparing documentation
* Identifying affected documentation
* Recording design decisions
* Recording reasoning
* Maintaining consistency across documentation

The developer remains the final reviewer of all documentation.

---

## Relationship with Source Code

The documentation should always remain consistent with the source code.

When the implementation changes:

* The **Current State** section should be updated.
* The **Design Evolution** section should receive a new dated entry describing the change.

Previous engineering decisions should never be silently removed.

---

## Intended Audience

The documentation is written for:

* The project developer
* Future contributors
* Future LLMs
* Viva examiners

Accordingly, the emphasis should be on documenting engineering decisions rather than merely describing the final application.
