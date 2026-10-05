---
name: hardware-requirements-engineer
description: >-
  Use this skill whenever the user is designing, specifying, selecting, or interfacing hardware — PCBs, interface/adapter boards, sensors, actuators, connectors, power supplies, embedded or IoT devices, communication buses — and before recommending any component, topology, or part number. It elicits and writes down testable functional requirements (electrical, interface/protocol, mechanical, environmental, safety, lifecycle, diagnostics) using a structured template with unique IDs, rationale, and acceptance criteria, so hardware choices stay traceable and don't get re-litigated after a board is fabricated. Trigger this even when the user only asks something like "what component should I use for X", "how do I interface Y with Z", "which sensor is best here", or "help me design a board that does W" — without explicitly saying "requirements" or "specifications". Capturing the requirement before the part number is the whole point — it's what prevents expensive rework once hardware is committed.
---

# Hardware Requirements Engineer

## Why requirements come before parts

Hardware commitments are expensive to reverse. A software bug is a redeploy; a wrong connector footprint, an undersized regulator, or a bus voltage mismatch is a PCB re-spin, a bill-of-materials change, or a part that goes end-of-life mid-production. The cost of discovering a missing constraint grows by an order of magnitude at each stage — cheap during a conversation, expensive after fabrication, very expensive after the first field failure.

So the job, before naming a single component or topology, is to make the requirement explicit, quantified, and written down. Not as bureaucracy — as insurance. A requirement that lives only as a vague adjective ("something robust", "low power") will get silently reinterpreted the next time the design is touched, by you or by the user. A requirement with an ID, a number, and a rationale survives that.

This doesn't mean interrogating the user before saying anything useful. It means treating "what do you actually need this to do, under what conditions, measured how" as the first-class deliverable — sometimes worked out inline in conversation, sometimes captured formally in a document — and treating "here's a part" as something that should trace back to it.

## Workflow

1. **Understand the system context first.** What does this hardware sit between? What's upstream and downstream — another board, a bus, a human, the outside world? What already exists that it must be compatible with? Don't skip this even if the user jumps straight to "which chip should I use" — the chip question can't be answered without it.

2. **Elicit requirements by category** (see below). Don't fire every question at once — that overwhelms and stalls the conversation. Ask in focused batches tied to what's actually undetermined, propose reasonable defaults when the domain suggests one ("I'll assume 12V nominal automotive supply with load-dump transients unless you tell me otherwise"), and let the user correct or confirm. If the user has already told you a category doesn't matter, don't reopen it.

3. **Draft requirements as testable statements**, not adjectives — each with an ID, a quantified statement, a rationale, and an acceptance criterion. See "Writing a testable requirement" below.

4. **Flag assumptions and open questions explicitly.** If you filled a gap with a reasonable default because the user hadn't specified it, mark it as `assumed`, not `confirmed`. Silent assumptions are exactly what this discipline exists to prevent.

5. **Only after requirements are captured — or the user explicitly says "just propose something," in which case proceed but still name your assumptions — move to solution and component selection.** Every proposed part or topology should reference which requirement IDs it satisfies and which, if any, it compromises on. This is also where you search to confirm each part actually meets what you're claiming for it — see "Confirm with research" below; it's not optional polish, it's the step that stops a plausible-sounding recommendation from being a wrong one.

## Requirement categories to probe

Not every project needs every category — use judgment about what's load-bearing for the task at hand. Skip a category quickly ("assuming standard indoor conditions, no vibration") rather than asking about it if it's clearly irrelevant.

**Electrical.** Supply voltage (nominal, min/max, transients — e.g. automotive 12/24V systems see load-dump and cranking transients per ISO 7637-2), current budget per rail, ripple/noise tolerance, isolation requirements, quiescent/sleep current if battery-powered.

**Interface / protocol.** Which buses (CAN, RS-485, I²C, SPI, UART, 1-Wire, analog 0–10V/4–20mA, discrete GPIO), signal levels, connector types and pinout constraints, cable length and the EMI environment it runs through, bus loading/termination.

**Timing & performance.** Latency budget, sample/refresh rate, resolution or precision needed, throughput, real-time constraints if any.

**Mechanical / physical.** Form factor and size envelope, mounting method, connector types (and whether they need to match existing harness connectors), IP/ingress rating, weight limits.

**Environmental.** Operating and storage temperature range, humidity, vibration/shock profile (a camper or vehicle install is not an office desk), altitude, exposure to condensation or fuel/chemical vapors if relevant.

**Safety & compliance.** Isolation classes, relevant standards or certifications (CE, E-mark, UL, etc. — only if the user's context calls for them), fail-safe behavior on power loss or fault, reverse-polarity/overcurrent protection expectations.

**Software / firmware interface.** What talks to this hardware (MCU, SBC, home-automation hub), protocol stack, configuration/update mechanism, expected API or register map, diagnostic/telemetry needs.

**Lifecycle & production.** Prototype quantity vs. eventual production volume, target unit cost, sourcing and lead-time constraints, second-source availability for critical parts — a one-off prototype and a 500-unit run justify very different component choices.

**Diagnostics & observability.** Status indication (LEDs, telemetry registers), test points, self-test or fault-reporting behavior — how will anyone know this board is working, or why it isn't.

## Writing a testable requirement

Each requirement gets: an ID, a category tag, a quantified statement, a rationale, an acceptance criterion, a priority, and a status.

Weak: "The board should handle automotive power."
Better: "**REQ-EL-003** (Electrical, Must, Confirmed) — The input stage shall accept 9–32 VDC continuous and survive load-dump transients up to 40V per ISO 7637-2 without damage. *Rationale:* powered directly from vehicle battery bus, no intermediate regulation upstream. *Acceptance:* input stage survives a simulated 40V/400ms load-dump pulse with no functional degradation afterward."

The difference is that the second version can be checked — by a reviewer, by a test, by the part's own datasheet — without asking the author what they meant.

Priority: use MoSCoW (Must / Should / Could / Won't) so trade-offs later have a basis.
Status: `confirmed` (user-stated), `assumed` (you inferred it — say so and why), or `open` (still needs an answer).

## Confirm with research, not just with memory or a lab bench

Before treating a technical unknown as something that only physical measurement or another round-trip with the user can resolve, spend a few minutes searching first. Datasheets, manufacturer application notes, and forum threads from people who already built the same interface frequently have the answer already — a device's real electrical protocol, a connector's pinout, a component's actual current rating under the duty cycle you care about. Jumping straight to "mark it `open`, verify on the bench" throws away information that was a search away, and it's the quiet way this whole discipline degrades: rigorous about the paperwork, careless about whether the paperwork is actually true.

This matters most in two places:

- **Component and sizing decisions.** Don't assert that a part satisfies a requirement — current rating, thermal derating, voltage tolerance, timing, mechanical fit — from memory or from a generic sense of what "that kind of part" usually does. Pull the actual datasheet, or find a documented build report (forum thread, teardown, application note) that used the part under comparable conditions, before writing it down as satisfying a REQ. A relay silkscreened "10A" may only hold that rating at 30°C ambient with a resistive load — automotive vibration and a hot engine bay change the real number, and only the datasheet or a field report says by how much. The same goes for wire gauge, connector current rating, regulator dropout under worst-case input voltage, and so on: anywhere a number is load-bearing for a decision, confirm the number, don't recall it.
- **Protocol and bus identification.** If a device's interface is only loosely described — "it's CAN," "it's I²C" — from the user or from a first guess, don't take the label at face value before proposing hardware around it. Search for whether that specific device or product family has already been reverse-engineered or documented by a user community; consumer, RV, and marine electronics very often use something that only resembles the standard it's named after. Finding that out from a forum thread is minutes of work; finding it out from a fried board after building the wrong front end is not.

When you find confirmation, cite it (link or source name) next to the requirement or recommendation it supports — this is also what fills in the "Fonti" style evidence a reviewer would want. When you look and can't find confirmation, say so plainly and keep the item `open` rather than quietly reverting to an assumption dressed up as verified.

## Producing the document

Once a meaningful set of requirements exists — not necessarily complete, but enough to be useful — write it to a file rather than leaving it only in the chat transcript. Follow the structure in `references/frd_template.md`. Keep it a living document: as the conversation surfaces new constraints or resolves an `open` item, update it rather than starting over.

Don't manufacture completeness. A short, honest requirements list with three `open` items is more useful than a padded one that invents specificity the user never gave you.

## Common pitfalls to avoid

- **Accepting adjectives without quantifying them.** "Small", "cheap", "low-power", "robust" are prompts for a follow-up question, not requirements.
- **Over-specifying.** Don't invent requirements in categories the user has explicitly waved off, and don't pad the document to look thorough — this project's guidance is to stay tightly scoped to what's asked.
- **Defaulting to office/indoor assumptions** for environmental and mechanical categories when the actual install environment (vehicle, marine, outdoor) is materially harsher.
- **Freezing an assumption as fact.** If you filled a gap yourself, it's `assumed` until the user confirms it — say so plainly rather than presenting it as given.
- **Proposing parts before the requirement exists.** If asked directly for a component recommendation with no context, it's fine to give a provisional answer, but pair it with the one or two requirement questions whose answers would most change the recommendation.
- **Marking something `open` and reaching for a bench measurement before searching for it.** A quick search is cheaper than a lab session and often already has the answer — treat physical verification as the fallback for what research didn't resolve, not the first move.
