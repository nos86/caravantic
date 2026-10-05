# Functional Requirements Document — Template

Use this structure when writing the requirements file. Omit sections that genuinely don't apply rather than leaving them as empty placeholders — an FRD with "N/A — not applicable, this board has no user-facing enclosure" is more honest than a blank heading.

```markdown
# [Board/System Name] — Functional Requirements

Status: Draft | Under Review | Confirmed
Last updated: [date]

## 1. Context and scope

One paragraph: what this hardware does, what it connects to upstream and downstream,
and what's explicitly out of scope.

## 2. Requirements

Group by category. Each requirement follows this format:

**REQ-[CAT]-[NNN]** (Category, Priority, Status)
Statement: [quantified, testable statement — "shall ..."]
Rationale: [why this constraint exists]
Acceptance criterion: [how you'd verify this is met]

Category tags: EL (electrical), IF (interface/protocol), TIM (timing/performance),
MECH (mechanical/physical), ENV (environmental), SAFE (safety/compliance),
SW (software/firmware interface), LIFE (lifecycle/production), DIAG (diagnostics).

Priority: Must | Should | Could | Won't (MoSCoW).
Status: Confirmed (user-stated) | Assumed (inferred — state the reasoning) | Open (unresolved).

### 2.1 Electrical
...

### 2.2 Interface / Protocol
...

### 2.3 Timing & Performance
...

### 2.4 Mechanical / Physical
...

### 2.5 Environmental
...

### 2.6 Safety & Compliance
...

### 2.7 Software / Firmware Interface
...

### 2.8 Lifecycle & Production
...

### 2.9 Diagnostics & Observability
...

## 3. Open questions

Numbered list of unresolved items blocking a Confirmed status, each tied to the
requirement ID(s) it affects.

## 4. Assumptions log

Every requirement marked Assumed, listed with the reasoning, so a later reviewer
can see at a glance what wasn't actually confirmed by the user.

## 5. Revision history

| Date | Change | Reason |
|------|--------|--------|
| ... | ... | ... |
```

## Notes on filling it in

- Number requirements sequentially within each category (REQ-EL-001, REQ-EL-002, ...). Don't renumber when one is removed — leave a gap, or mark it `[REMOVED — superseded by REQ-EL-004]` so history stays legible.
- The acceptance criterion should be something a third party could check without asking the author what they meant. "Works reliably" is not an acceptance criterion; "maintains CAN bus communication with <1% frame loss over a 2-hour 0–60°C thermal cycle" is.
- Keep the document proportional to the project. A single sensor breakout board doesn't need nine populated categories — three or four well-written requirements beat nine sparse, padded ones.
