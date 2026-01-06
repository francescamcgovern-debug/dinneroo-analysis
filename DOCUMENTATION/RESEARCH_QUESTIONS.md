# Research Questions

## How to Use This Document

This is the **single source of truth** for research questions. All analysis should map to a question here.

### Adding a New Question

When you get a brief from Anna or anyone else, add it here using this template:

```markdown
### Q[N]: [Question text]

| Field | Value |
|-------|-------|
| **Requested by** | [Name] |
| **Date added** | [YYYY-MM-DD] |
| **Priority** | High / Medium / Low |
| **Agent** | Dish / Zone / Customer / Gap |
| **Output** | Report / Dashboard / Both |
| **Status** | Open / In Progress / Answered |
| **Deliverable** | [Link to output file when complete] |

**Context:** [Any additional context from the requester]

**Answer:** [Summary of findings when complete]
```

---

## Active Questions

### Q1: What is an MVP Zone? (Primary Question)

| Field | Value |
|-------|-------|
| **Requested by** | Francesca |
| **Date added** | 2026-01-05 |
| **Priority** | High |
| **Agent** | Dish + Zone |
| **Output** | Dashboard + Report |
| **Status** | Open |
| **Deliverable** | TBD |

**Goal:** Define the MINIMUM VIABLE ZONE - what a zone needs to be successful.

**Sub-questions:**
1. **Partners:** What's the minimum number of partners a zone needs?
2. **Cuisines:** Which cuisines must be represented? (Not limited to what OG survey asked)
3. **Dishes:** Which dishes are essential? (Discover from actual orders + open-text, not survey rankings)
4. **Presentation:** How should dishes be presented to be family-friendly?

**Key constraint:** We want to discover dishes/cuisines BEYOND what the original survey asked about. Use behavioral data (orders) and open-text feedback to find opportunities.

**Answer:** [To be completed]

---

### Q2: Which dishes should we recommend? (Dish Discovery)

| Field | Value |
|-------|-------|
| **Requested by** | Francesca |
| **Date added** | 2026-01-05 |
| **Priority** | High |
| **Agent** | Dish |
| **Output** | Report |
| **Status** | Open |
| **Deliverable** | TBD |

**Goal:** Identify dishes to recommend that go BEYOND the OG survey list.

**Approach:**
1. Analyze `MENU_ITEM_LIST` in orders - what's actually being ordered?
2. Extract dish mentions from open-text (post-order, dropoff, ratings)
3. Mine customer transcripts for unprompted dish/cuisine mentions
4. Compare to current catalog - what's working, what's missing?

**DO NOT USE:** OG Survey dish rankings

**Answer:** [To be completed]

---

### Q3: How should dishes be presented to be family-friendly?

| Field | Value |
|-------|-------|
| **Requested by** | Francesca |
| **Date added** | 2026-01-05 |
| **Priority** | High |
| **Agent** | Dish |
| **Output** | Report |
| **Status** | Open |
| **Deliverable** | TBD |

**Goal:** Understand how to present dishes so families will order them.

**Sources:**
- Post-order survey (family segment feedback)
- Customer transcripts (family interviews)
- WBRs (partner execution capabilities)

**Answer:** [To be completed]

---

## Question Backlog

*Questions that have been identified but not yet prioritized*

### QB1: Which zones should we prioritize for expansion?

| Field | Value |
|-------|-------|
| **Requested by** | TBD |
| **Date added** | 2026-01-05 |
| **Priority** | Medium |
| **Agent** | Gap |
| **Output** | TBD |
| **Status** | Backlog |

---

### QB2: Who are our most valuable customers?

| Field | Value |
|-------|-------|
| **Requested by** | TBD |
| **Date added** | 2026-01-05 |
| **Priority** | Medium |
| **Agent** | Customer |
| **Output** | TBD |
| **Status** | Backlog |

---

### QB3: Why are some zones underperforming despite good supply?

| Field | Value |
|-------|-------|
| **Requested by** | TBD |
| **Date added** | 2026-01-05 |
| **Priority** | Medium |
| **Agent** | Zone |
| **Output** | TBD |
| **Status** | Backlog |

---

## Completed Questions

*Move questions here when answered*

[None yet]

---

## Question Guidelines

### What Makes a Good Research Question?

- **Specific** - Clear scope, not too broad
- **Answerable** - Can be addressed with available data
- **Actionable** - Answer will inform a decision
- **Measurable** - Success criteria are clear

### Bad vs Good Questions

| Bad | Good |
|-----|------|
| "How are we doing?" | "What's our satisfaction rate by zone?" |
| "What should we do?" | "Which zones should we prioritize for partner expansion?" |
| "Why don't people order?" | "What barriers do dropoffs cite for not ordering?" |

### When to Create a New Question

- You receive a brief from a stakeholder
- Analysis reveals a follow-up question
- A finding raises new questions
- Business context changes

---

## Routing Reference

| Question About | Route To |
|----------------|----------|
| Dishes, cuisines, menus, food | Dish Agent |
| Zones, areas, geography, performance | Zone Agent |
| Customers, segments, families | Customer Agent |
| Gaps, opportunities, expansion | Gap Agent |

---

*Keep this document updated. It's the roadmap for all analysis.*

