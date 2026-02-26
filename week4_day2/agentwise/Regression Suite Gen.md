# Impact-Based Regression Suite Generator Agent
## Technical Architecture Design
Version: 1.0
Author: AI Agentic Architect
Status: Approved (Human-in-Loop Validated)

---

# 1. Objective

Generate an **impact-based regression suite** when a new user story is introduced.

Primary Inputs:
- Structured User Stories (Given/When/Then + AC)
- Excel-based Test Repository (with Story ID mapping)
- Optional Defect CSV (risk enrichment)

Output:
- Ranked regression suite
- AI-generated draft tests (if coverage gaps detected)
- Full decision graph audit trail

---

# 2. System Architecture Overview

Architecture Type:
Multi-Agent Orchestrated System

Deployment Phases:
Phase 1: Local (VS Code Extension + ChromaDB)
Phase 2: Azure AI Search Migration

Core Layers:
1. Interface Layer (VS Code Extension)
2. Orchestrator Layer
3. Specialized AI Agents
4. Vector Store Abstraction Layer
5. Audit & Governance Store

---

# 3. Agent Architecture

## 3.1 Orchestrator Agent
Controls execution order and human approval checkpoints.

Pipeline:
1. Ingestion Agent
2. Domain Classification Agent
3. Embedding Agent
4. Retrieval Agent
5. AC Coverage Agent
6. Ranking Agent
7. Generation Agent (if needed)
8. Audit Agent

Human approval required after:
- Domain classification
- Candidate retrieval
- Ranking output
- Generation output

---

## 3.2 Ingestion Agent

Input:
- New User Story (Given/When/Then structured)

Output:
- Parsed AC list
- Structured story object

---

## 3.3 Domain Classification Agent

Function:
Classify story into Functional Domain.

Method:
- Embedding similarity against domain taxonomy
OR
- Configurable keyword YAML rules

Human confirmation required.

---

## 3.4 Embedding Agent

Embeddings Generated For:

1. Story-level vector
2. Acceptance Criteria vectors (individual)
3. Test case vectors

Storage:
VectorAdapter Interface:
- LocalVectorAdapter (ChromaDB)
- AzureVectorAdapter (Future)

---

## 3.5 Retrieval Agent

Process:
1. Story vector → Retrieve similar stories
2. AC vectors → Retrieve similar test cases
3. Direct mapping from Excel
4. Semantic expansion across repository

No regression size cap.

---

## 3.6 AC Coverage Agent

Rule:
Minimum 50% AC overlap required.

Coverage Ratio:
Matched_AC / Total_AC ≥ 0.5

Produces:
AC similarity matrix
Coverage ratio per test case

---

## 3.7 Ranking Agent

Enterprise Multi-Factor Model:

Final Score =
W1 × Semantic Similarity
+ W2 × AC Coverage Density
+ W3 × Defect Density
+ W4 × Module Criticality
+ W5 × Regression Recurrence

Dynamic threshold + human override enabled.

Output:
Ranked regression list (no explanation noise).

---

## 3.8 Generation Agent

Triggered when:
AC coverage < threshold.

Guardrails:
- Strict Given/When/Then format
- Must reference specific AC IDs
- No expansion beyond story scope
- Flag as AI-generated

Human approval mandatory.

---

## 3.9 Audit & Governance Agent

Stores:
- Similarity scores
- AC coverage matrix
- Threshold decisions
- Ranking breakdown
- Generation prompts
- Final regression suite

Does NOT store:
- Raw embeddings
- Chain-of-thought reasoning

---

# 4. Threshold Governance Model

1. Dynamic baseline threshold
2. Percentile fallback
3. Human override capability
4. Audit logging

---

# 5. Human-in-the-Loop Checkpoints

Phase Gates:
1. Story parsing approval
2. Domain confirmation
3. Retrieval candidate approval
4. Ranking approval
5. AI generation approval

No autonomous finalization allowed.

---

# 6. Storage Design

Vector Store:
- ChromaDB (local)
- Azure AI Search (future)

Metadata Store:
- SQLite (local)
- Azure SQL / Cosmos (future)

Audit Store:
- JSON execution logs per run

---

# 7. VS Code Extension Architecture

Components:
- Story input panel
- Phase approval UI
- Regression ranking viewer
- AC coverage visualization
- AI generation review panel

Backend:
- Python FastAPI local server
- REST calls from extension

---

# 8. Future Azure Migration Strategy

Replace:
LocalVectorAdapter → AzureVectorAdapter

No change required in:
- Agent prompts
- Ranking logic
- Governance logic

Cloud scaling ready.

---

# 9. Non-Functional Requirements

- Deterministic prompts
- Zero hallucination expansion
- Transparent audit trail
- Configurable weights
- Pluggable vector backend
- Modular agent design

---

# 10. Risk Controls

- AC-bound generation
- 50% minimum coverage
- Human approval at every phase
- No size-based truncation
- No automatic threshold locking

---

# 11. Execution Flow Summary

New Story →
Parse →
Classify →
Embed →
Retrieve →
Filter by AC Coverage →
Rank →
Human Approve →
Generate (if needed) →
Human Approve →
Export Regression Suite →
Store Decision Graph

---

# End of Document