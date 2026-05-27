# Agent Instructions

These instructions apply to all AI agents working in this repository.

## Project

ChordLens is a local-first music creation tool with two planned MVP modes:

- `AR Chord Looper`: webcam-based two-hand chord loop creation.
- `Audio Analysis Studio`: upload-based stem separation, chord analysis, and cover-song practice.

The project is intended to run locally first. Do not add cloud deployment, user accounts, YouTube audio extraction, or paid external services unless Peter explicitly approves that direction.

## Required Approval Gates

Before making any change that adds, removes, rewrites, or significantly changes primary functionality, ask Peter for approval.

This includes:

- New application features.
- Large UI changes.
- Major architecture changes.
- Data model changes.
- Build system or framework changes.
- Dependency changes that affect runtime behavior.
- Deleting or replacing existing functionality.

Small typo fixes, documentation clarifications, and narrow non-behavioral cleanup can be made directly, but summarize them clearly.

## Spec And Plan Workflow

For approved feature work or substantial changes:

1. Use the relevant Superpower skills before implementation.
2. Write or update a spec first.
3. Write an implementation plan after the spec is accepted.
4. Wait for Peter's approval before writing code.
5. Implement against the approved plan.
6. Verify the change with appropriate tests, builds, and manual checks.

Do not skip the spec and plan process for major work, even if the change seems straightforward.

## Commit And Push Policy

Do not commit until Peter has completed code review and explicitly approved the commit.

Do not push until Peter explicitly approves the push.

When approval is given:

- Keep commits focused and intentionally named.
- Do not include unrelated changes.
- Mention verification performed in the final summary.

## UI Review Policy

When designing web pages or significant UI flows, agents may use the `ui-ux-pro-max` and `huashu-design` skills to support UI/UX direction, interaction design, and visual exploration.

Before implementing a significant UI direction:

1. Create temporary HTML design options or prototypes for Peter to review.
2. Present the options clearly and ask Peter to choose or request changes.
3. Do not implement the selected direction in the product code until Peter approves the design.

After implementing UI work, ask Peter whether to connect Chrome for UI/UX and functional inspection.

If Peter agrees:

1. Use the Chrome tooling to inspect the running UI.
2. Check layout, responsiveness, interaction behavior, visual polish, and obvious accessibility issues.
3. Fix issues found during inspection directly.
4. Re-check the affected UI after fixes.
5. Summarize what was inspected and what was fixed.

If Peter declines Chrome inspection, perform the best available local verification and state the limitation.

## Product Boundaries

Do not implement YouTube audio downloading or extraction. ChordLens may use uploaded audio files and local authorized media sources.

Keep V1 local-first:

- Local frontend and backend.
- Local audio processing.
- Local project files.
- No account system.
- No cloud storage requirement.

Treat audio analysis as best-effort. Do not present BPM, key, chord, stem, or transcription results as guaranteed perfect.

## Engineering Guidelines

- Prefer simple, local, inspectable implementations for V1.
- Keep AR Looper and Audio Studio as independent pages until Peter approves deeper integration.
- Avoid full DAW scope unless explicitly planned.
- Avoid broad refactors that are not required for the approved task.
- Preserve user changes and do not revert unrelated work.
- Use repository patterns once implementation exists.
- Keep documentation aligned with actual behavior.

## Verification Expectations

Use verification proportional to the change:

- Documentation: review rendered Markdown structure and links where practical.
- Frontend: run build/tests and inspect UI when available.
- Backend: run unit tests and any targeted pipeline checks available.
- Audio processing: verify with small sample files before claiming end-to-end success.
- AR behavior: verify camera permission flow, hand tracking state, hover commit, cooldown, and audio feedback.

If verification cannot be run, state exactly what was not run and why.
