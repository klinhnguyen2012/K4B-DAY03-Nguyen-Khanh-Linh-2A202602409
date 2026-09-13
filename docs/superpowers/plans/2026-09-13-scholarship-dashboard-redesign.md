# Scholarship Dashboard Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the prototype landing-style interface with a responsive Scholarship Planning dashboard that exposes the profile-to-application flow.

**Architecture:** Keep the single React `App` component because this prototype has one screen and local data only. Use state for the selected scholarship, detail view, comparison mode, task completion, and chat messages. Replace the existing condensed stylesheet with structured CSS sections and responsive breakpoints.

**Tech Stack:** React 19, Vite 6, plain CSS, existing local PNG illustration.

## Global Constraints

- Keep purple branding and `/assets/scholarship-vector-right.png`.
- Do not show internal scholarship IDs or mock/debug copy in the user interface.
- Only render Application Plan after a scholarship is selected.
- Preserve the existing Vite build and Sites packaging workflow.

---

### Task 1: Define dashboard data and interactions

**Files:**
- Modify: `scholarship-prototype/src/App.jsx`

**Interfaces:**
- Consumes: local scholarship/profile data and `useState`.
- Produces: `selectedScholarship`, `comparisonEnabled`, `completedTasks`, and `messages` state used by dashboard sections.

- [ ] **Step 1: Replace internal IDs with presentation data**

Create scholarship objects with name, match score, school, country, funding, requirements, gap, deadline, and plan tasks. Keep machine-only IDs out of rendered copy.

- [ ] **Step 2: Implement user actions**

Add controls for details, comparison and plan creation. Plan creation sets the selected scholarship and scrolls to `#application-plan`.

- [ ] **Step 3: Add flow, profile, agent analysis, matches, and gap sections**

Render semantic sections in the order specified by the approved design.

- [ ] **Step 4: Conditionally render the application plan**

Render the plan only when `selectedScholarship` is not null. Wire checkboxes to update the completion count and task state.

### Task 2: Replace visual system and responsive layout

**Files:**
- Modify: `scholarship-prototype/src/styles.css`

**Interfaces:**
- Consumes: class names from `App.jsx`.
- Produces: responsive desktop, tablet, and mobile dashboard layout.

- [ ] **Step 1: Establish readable typography and tokens**

Use CSS variables, explicit `line-height`, and normal letter spacing for Vietnamese content.

- [ ] **Step 2: Build a compact hero and five-step flow bar**

Keep the local illustration on the right, reduce hero height, and use a scrollable flow bar on narrow screens.

- [ ] **Step 3: Style cards, gap statuses, and conditional plan**

Add visual hierarchy for match score, funding, requirements, gaps, deadline reminders, CTA groups, task statuses, and completion progress.

- [ ] **Step 4: Add responsive breakpoints**

Collapse multi-column sections at 1024px and one-column sections at 720px; retain controls with accessible hit areas.

### Task 3: Verify the UI artifact

**Files:**
- Test: `scholarship-prototype/tests/sites-worker.test.mjs`

- [ ] **Step 1: Build the production artifact**

Run: `npm run build`

Expected: Vite produces `dist/client` and the Sites build preparation completes.

- [ ] **Step 2: Run the existing Sites tests**

Run: `npm run test:sites`

Expected: all four asset, fallback, API, and packaging tests pass.

- [ ] **Step 3: Verify the preview asset**

Run: `curl -fsSI http://127.0.0.1:4174/assets/scholarship-vector-right.png`

Expected: HTTP 200 with `Content-Type: image/png`.

- [ ] **Step 4: Commit**

Run: `git add scholarship-prototype/src/App.jsx scholarship-prototype/src/styles.css docs/superpowers/plans/2026-09-13-scholarship-dashboard-redesign.md && git commit -m "feat: redesign scholarship dashboard"`
