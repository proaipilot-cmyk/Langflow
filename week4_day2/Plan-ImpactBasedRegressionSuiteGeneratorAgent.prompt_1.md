# Impact-Based Regression Suite Generator Agent System - Implementation Plan

**TL;DR**  
Build a stateless FastAPI backend with 8 Anthropic Claude agents executing sequentially (Ingestion → Domain Classification → Embedding → Retrieval → AC Coverage → Ranking → Generation → Audit). Separate HTTP endpoints per phase with manual human approval gates. SQLite stores metadata, approvals, and audit logs. ChromaDB (via VectorAdapter abstraction) persists embeddings. VS Code Extension (5 panels) provides UI, maintains local run history, communicates HTTP/JSON only—no embedded business logic.

---

## Planning Summary

### Architecture Overview

**Phase Execution Flow**
```
Story Input → Ingestion → Domain Classification → Embedding → Retrieval → AC Coverage → Ranking → Generation (conditional) → Audit
```

**Key Design Decisions**
- **Stateless API**: Each request includes full story + prior outputs; no session memory between requests
- **Separate HTTP endpoints per phase**: `/phase/{phase_name}/execute` pattern
- **Manual approval gates**: Extension UI blocks until human approves phase output before next phase runs
- **ChromaDB persistence**: Embeddings stored per run; Retrieval queries within same run's collection
- **Audit trail**: Logs all phase inputs/outputs, vector similarity scores, and Generation conditioning data
- **Extension local history**: VS Code Extension caches run history; API is source of truth for data
- **Generation trigger**: Ranking score must exceed configurable threshold (suggest ≥0.7) to make Generation panel visible
- **Error handling strategy**: Pause + require human decision; optional auto-retry for transient API failures
- **Anthropic Claude**: All agents use same LLM backend (configurable model in config.py)

---

## API Layer Implementation

### FastAPI Application Structure

**`backend/app.py`**
- Root FastAPI application instance
- CORS middleware configuration
- Global error handling middleware
- Request logging middleware

**`backend/config.py`**
- Environment variables (Anthropic API keys, DB paths, model config)
- Model enum for Anthropic Claude models (claude-3-opus, claude-3-sonnet, etc.)
- Logging configuration
- Configurable phase parameters (Generation threshold, timeouts)

### Request/Response Models (Pydantic Schemas)

**`backend/schemas/common.py`**
- `StoryInput` — original story/requirements text, metadata
- `PhaseInput` — story + prior phase outputs (cumulative context)
- `PhaseOutput` — agent result + metadata (execution time, token usage, etc.)
- `ApprovalDecision` — human approval with optional feedback/rejection reason
- `RankingScoreMetadata` — threshold and actual score from Ranking phase

**`backend/schemas/requests.py`**
- `IngestionRequest` — raw story text, optional metadata
- `DomainClassificationRequest` — story + ingestion output
- `EmbeddingRequest` — story + classification output
- `RetrievalRequest` — story + embeddings + query context
- `ACCoverageRequest` — story + retrieval results
- `RankingRequest` — story + AC coverage data
- `GenerationRequest` — story + ranking results (conditional)
- `AuditRequest` — run summary with all phase outputs

**`backend/schemas/responses.py`**
- `IngestionResponse` — parsed requirements, acceptance criteria, scope, extracted structured data
- `DomainClassificationResponse` — domain labels (API/UI/DB/etc), confidence scores, testing scope
- `EmbeddingResponse` — vector dimensions, embedding metadata, storage status
- `RetrievalResponse` — matched test cases, similarity scores, relevance ranking
- `ACCoverageResponse` — coverage gaps, risk matrix, uncovered requirements
- `RankingResponse` — ranked items (ordered by priority/impact), scores, reasoning
- `GenerationResponse` — generated test cases with metadata, conditioning inputs applied
- `AuditResponse` — audit log entry with full traceability

### Agent Base Class & Interface

**`backend/agents/base.py`**
- `BaseAgent` abstract class
  - `execute(context: PhaseInput) -> PhaseOutput` — main execution method
  - `validate_input(context: PhaseInput) -> bool` — input validation
  - Error handling contract (raise `PhaseExecutionError` on failure)
  - Dependency injection for config, vector adapter, repository access

### Agent Implementations (8 agents)

**`backend/agents/ingestion_agent.py`**
- `IngestionAgent(BaseAgent)`
- Parse story text for structured requirements
- Extract user stories, acceptance criteria, test scenarios
- Return: `IngestionResponse`

**`backend/agents/domain_agent.py`**
- `DomainClassificationAgent(BaseAgent)`
- Classify domain (Frontend/API/Database/Infrastructure/Integration)
- Determine testing scope and affected systems
- Return: `DomainClassificationResponse`

**`backend/agents/embedding_agent.py`**
- `EmbeddingAgent(BaseAgent)`
- Generate embeddings for requirements using Anthropic (or via embeddings library if available)
- Delegate storage to VectorAdapter
- Record metadata in VectorRepository
- Return: `EmbeddingResponse`

**`backend/agents/retrieval_agent.py`**
- `RetrievalAgent(BaseAgent)`
- Query ChromaDB for similar test cases using embeddings
- Score relevance using ChromaDB similarity scores
- Return: `RetrievalResponse`

**`backend/agents/coverage_agent.py`**
- `ACCoverageAgent(BaseAgent)`
- Analyze retrieved test cases vs AC requirements
- Identify coverage gaps (which ACs have no test cases)
- Build risk matrix (gap severity × requirement importance)
- Return: `ACCoverageResponse`

**`backend/agents/ranking_agent.py`**
- `RankingAgent(BaseAgent)`
- Rank retrieved test cases by priority/impact using Anthropic reasoning
- Return score for Generation gate (0.0–1.0)
- Return: `RankingResponse` with `score` field

**`backend/agents/generation_agent.py`**
- `GenerationAgent(BaseAgent)`
- Generate new test cases matching requirements
- Conditioned on ranking score + coverage data (passed from prior phases)
- Only reachable if Ranking score ≥ threshold
- Return: `GenerationResponse`

**`backend/agents/audit_agent.py`**
- `AuditAgent(BaseAgent)`
- Create audit log entry with full run data
- Record all inputs, outputs, decisions, vector scores, conditioning context
- Return: `AuditResponse`

### Orchestrator

**`backend/orchestrator.py`**
- `Orchestrator` class
  - Coordinates phase execution sequence
  - Enforces stateless request flow (validates prior outputs included in context)
  - Validates prerequisites before each phase (e.g., Ranking must run before Generation)
  - Handles error states (raises exception, client must resubmit with human decision)
  - No state stored between requests

### Vector Storage Abstraction

**`backend/storage/vector_adapter.py`**
- `VectorAdapter` abstract interface
  - `store(vectors: List[Vector], metadata: Dict) -> str` (returns collection_id)
  - `search(query_vector: Vector, k: int) -> List[SearchResult]` (returns top-k matches with scores)
  - `delete(collection_id: str) -> void`
  - `get_collection(collection_id: str) -> Collection` (for debugging/inspection)

**`backend/storage/chroma_adapter.py`**
- `ChromaAdapter(VectorAdapter)`
- Implements ChromaDB integration
- Collection management (per-run collections)
- Metadata embedding and retrieval

### Agent Factory

**`backend/agents/agent_factory.py`**
- `AgentFactory` class
  - `get_agent(phase_name: str) -> BaseAgent` factory method
  - Agent instantiation with dependency injection
  - Config, vector adapter, repositories passed to agents

### API Route Handlers

**`backend/routes/phase_routes.py`** — 8 endpoints, one per phase
- `POST /phase/ingestion` → IngestionAgent
- `POST /phase/classification` → DomainClassificationAgent
- `POST /phase/embedding` → EmbeddingAgent
- `POST /phase/retrieval` → RetrievalAgent
- `POST /phase/coverage` → ACCoverageAgent
- `POST /phase/ranking` → RankingAgent
- `POST /phase/generation` → GenerationAgent (conditional: checks Ranking score ≥ threshold; returns 403 Forbidden if threshold not met)
- `POST /phase/audit` → AuditAgent

Each endpoint:
- Logs request to audit trail
- Calls orchestrator to validate prerequisites
- Executes agent
- Records phase execution in database
- Returns response

**`backend/routes/approval_routes.py`**
- `POST /approval/{phase_name}` → Submit human approval decision
  - Requires: phase_name, run_id, approved (bool), feedback (optional)
  - Updates ApprovalGate record
- `GET /approval/{phase_name}/{run_id}` → Check approval status
  - Returns: approval_status, feedback, decided_at, decided_by

**`backend/routes/history_routes.py`**
- `GET /runs` → List recent runs (limit parameter)
- `GET /runs/{run_id}` → Get full run with all phase executions
- `DELETE /runs/{run_id}` → Soft-delete run (optional)

**`backend/routes/health_routes.py`**
- `GET /health` → Service health check (DB connected, ChromaDB accessible)

---

## Database Layer Implementation

### SQLAlchemy ORM Models

**`backend/database/models.py`**

```
Run
├── id: UUID (PK)
├── story_text: TEXT
├── created_at: TIMESTAMP
├── status: ENUM (in_progress, completed, failed)
└── Relationships: phases[], approvals[], audit_logs[]

PhaseExecution
├── id: UUID (PK)
├── run_id: UUID (FK → Run)
├── phase_name: STRING (ingestion, classification, embedding, retrieval, coverage, ranking, generation, audit)
├── input_data: JSON
├── output_data: JSON
├── status: ENUM (pending, executed, approved, rejected, failed)
├── executed_at: TIMESTAMP (nullable)
├── error_message: TEXT (nullable)
└── Relationships: approval_gate, audit_logs[]

ApprovalGate
├── id: UUID (PK)
├── phase_execution_id: UUID (FK → PhaseExecution)
├── phase_name: STRING
├── approval_status: ENUM (pending, approved, rejected)
├── human_feedback: TEXT (nullable)
├── decided_at: TIMESTAMP (nullable)
├── decided_by: STRING (nullable, username/email)
└── created_at: TIMESTAMP

VectorMetadata
├── id: UUID (PK)
├── run_id: UUID (FK → Run)
├── embedding_id: STRING (ChromaDB collection reference)
├── source_text: TEXT (original text that was embedded)
├── vector_collection: STRING (ChromaDB collection name)
├── created_at: TIMESTAMP
└── Relationships: run

AuditLog
├── id: UUID (PK)
├── run_id: UUID (FK → Run)
├── phase_name: STRING
├── event_type: ENUM (phase_start, phase_complete, approval_decision, error, generation_gated)
├── details: JSON (event-specific data: inputs, outputs, scores, conditioning, error traces)
├── created_at: TIMESTAMP
└── Relationships: run
```

### Database Session Management

**`backend/database/session.py`**
- `get_db_session()` — FastAPI dependency providing SQLAlchemy session
- Database connection pooling configuration
- Transaction context managers for atomic operations

### Repository Pattern (Data Access Layer)

**`backend/repositories/run_repository.py`**
- `RunRepository` class
  - `create_run(story_text: str) -> Run`
  - `get_run(run_id: str) -> Run`
  - `list_runs(limit: int) -> List[Run]`
  - `update_run_status(run_id: str, status: str) -> void`

**`backend/repositories/phase_repository.py`**
- `PhaseRepository` class
  - `record_phase_execution(run_id, phase_name, input_data, output_data) -> PhaseExecution`
  - `get_phase_execution(run_id, phase_name) -> PhaseExecution`
  - `update_phase_status(phase_exec_id, status) -> void`
  - `get_phase_inputs(run_id, phase_name) -> Dict` (returns cumulative context for next phase)

**`backend/repositories/approval_repository.py`**
- `ApprovalRepository` class
  - `create_approval_gate(phase_exec_id, phase_name) -> ApprovalGate`
  - `get_approval_gate(phase_exec_id) -> ApprovalGate`
  - `submit_approval_decision(gate_id, approved: bool, feedback: str) -> void`
  - `get_pending_approvals(run_id) -> List[ApprovalGate]`

**`backend/repositories/vector_repository.py`**
- `VectorRepository` class
  - `record_embedding(run_id, embedding_id, source_text, collection) -> void`
  - `get_vectors_for_run(run_id) -> List[VectorMetadata]`

**`backend/repositories/audit_repository.py`**
- `AuditRepository` class
  - `log_event(run_id, phase_name, event_type, details) -> void`
  - `get_audit_trail(run_id) -> List[AuditLog]` (ordered by created_at)

### Database Initialization

**`backend/database/init.py`**
- `init_db()` — Create all SQLAlchemy tables on startup
- Alembic migration setup (optional, for schema versioning in later phases)

---

## Web/Interface Layer (VS Code Extension)

### Extension Project Structure

**`extension/package.json`**
- Extension metadata (name, version, publisher)
- Dependencies (vscode, axios for HTTP, etc.)
- Contribution points:
  - View containers: `storyInput`, `approval`, `rankingViewer`, `acCoverage`, `generationReview`
  - Commands: `extension.startNewRun`, `extension.approvePhase`, `extension.rejectPhase`, etc.
- Icon and theme assets

**`extension/src/extension.ts`**
- `activate(context)` — Initialize extension on load
  - Register command handlers
  - Initialize PanelManager
  - Restore run history from cache
  - Set up state listeners
- `deactivate()` — Cleanup on unload

### HTTP Client

**`extension/src/api/apiClient.ts`**
- `ApiClient` class
  - Base HTTP client (axios instance with configured timeouts)
  - Configuration: backend URL (default: localhost:8000), retry policy
  - Methods:
    - `executePhase(phaseName: string, input: PhaseInput) -> Promise<PhaseOutput>` 
      - POST `/phase/{phaseName}`
      - Retry logic: 3× exponential backoff for 429/500/503; fail immediately on 401/403/404
    - `submitApproval(phaseName: string, run_id: string, decision: ApprovalDecision) -> Promise<void>`
      - POST `/approval/{phaseName}`
    - `getRunHistory(limit?: int) -> Promise<List<Run>>`
      - GET `/runs?limit={limit}`
    - `getRun(runId: string) -> Promise<Run>`
      - GET `/runs/{runId}`
  - Error handling: Throw user-friendly errors, log to Output channel

### Local State Management

**`extension/src/state/runCache.ts`**
- `RunCache` class
  - In-memory cache of recent runs
  - Persistence to VSCode ExtensionContext (globalState/workspaceState)
  - Methods:
    - `addRun(run: Run) -> void`
    - `getRun(runId: string) -> Run | null`
    - `listRuns() -> List<Run>`
    - `clearCache() -> void`

**`extension/src/state/stateManager.ts`**
- `StateManager` singleton class (Pub/Sub pattern)
  - Centralized state for current run
  - Current phase tracking
  - Approval status tracking
  - Methods:
    - `startRun(story: string) -> Promise<void>` (creates Run, executes Ingestion)
    - `executePhase(phaseName: string) -> Promise<void>` (call apiClient, update state)
    - `approvePhase(phaseName: string, feedback?: string) -> Promise<void>`
    - `rejectPhase(phaseName: string, reason: string) -> Promise<void>`
    - `subscribe(listener: (state) => void) -> unsubscribe_fn`
    - `getState() -> CurrentRunState`

### Panel Manager & Webview Orchestration

**`extension/src/panelManager.ts`**
- `PanelManager` class
  - Manages all 5 webview panels
  - Methods:
    - `showPanel(panelName: string) -> void`
    - `hidePanel(panelName: string) -> void`
    - `updatePanelData(panelName: string, data: any) -> void`
    - `registerPanel(panelName: string, webviewProvider: any) -> void`
  - Subscribes to StateManager; broadcasts state to all panels via postMessage

### Panel Components (5 Independent Panels)

**`extension/src/panels/storyInputPanel.ts`**
- `StoryInputPanel` class (WebviewProvider)
  - Text editor for story/requirements input
  - Real-time validation warnings (empty story, very long story)
  - Button: "Submit Story & Start Ingestion"
  - Displays ingestion output (parsed requirements, scope)
  - Listens to StateManager for phase completion

**`extension/src/panels/approvalPanel.ts`**
- `ApprovalPanel` class (WebviewProvider)
  - Display current phase output in read-only format
  - Show approve/reject UI
  - Feedback textarea for human comments
  - Submit button calls StateManager.approvePhase() or rejectPhase()
  - Displays phase name, execution timestamp, error (if any)

**`extension/src/panels/rankingViewerPanel.ts`**
- `RankingViewerPanel` class (WebviewProvider)
  - Display ranked test cases (from Ranking phase output)
  - Score visualization (bar chart or sparkline per item)
  - Show ranking reasoning from agent
  - Sortable table (by rank, score, name)
  - Hidden until Ranking phase completes
  - Show current ranking score in header (for Generation gate decision)

**`extension/src/panels/acCoveragePanel.ts`**
- `ACCoveragePanel` class (WebviewProvider)
  - Coverage gap display (unmet acceptance criteria)
  - Risk matrix visualization (heatmap: gap severity × requirement importance)
  - Show covered vs uncovered ACs
  - Bar chart: coverage percentage
  - Hidden until Coverage phase completes

**`extension/src/panels/generationReviewPanel.ts`**
- `GenerationReviewPanel` class (WebviewProvider)
  - Display generated test cases (syntax-highlighted code blocks)
  - Edit-in-place for minor changes
  - Accept/Discard buttons for generated content
  - Show conditioning inputs in collapsible section:
    - Ranking score that triggered generation
    - Coverage gaps that informed generation
    - Top-ranked test cases for reference
  - Hidden if Ranking score < threshold; shown otherwise (if module reaches Generation)

### Webview HTML Templates & Styling

**`extension/src/views/storyInput.html`**
- Textarea for story input
- Validation messages
- Submit button
- Output area for ingestion results

**`extension/src/views/approval.html`**
- Phase name and timestamp
- Output data (formatted JSON or summary)
- Error message (if phase failed)
- Approve/Reject buttons
- Feedback textarea

**`extension/src/views/rankingViewer.html`**
- Table of ranked items
- Bar chart for scores (Chart.js)
- Ranking reasoning text
- Current ranking score display

**`extension/src/views/acCoverage.html`**
- Heatmap of coverage (Chart.js or similar)
- Coverage percentage bar
- List of uncovered ACs
- Risk matrix table

**`extension/src/views/generationReview.html`**
- Generated test cases (syntax highlighting: Highlight.js)
- Conditioning context (collapsible)
- Edit/Accept/Discard buttons
- Copy-to-clipboard for generated code

### Utilities

**`extension/src/utils/logger.ts`**
- Log to VS Code Output channel ("Impact-Based Regression Suite" channel)
- Severity levels: info, warn, error

**`extension/src/utils/validators.ts`**
- `validateStoryInput(text: string) -> { valid: bool, errors: string[] }`
- `validatePhaseOutput(output: any, phaseName: string) -> { valid: bool, errors: string[] }`

---

## Implementation Sequence & Testability

### Phase 1: Backend Foundation (Order Critical)
1. ✅ `config.py` + `app.py` — FastAPI root
2. ✅ `schemas/{common, requests, responses}.py` — Data contracts
3. ✅ `agents/base.py` — Agent interface
4. ✅ `storage/{vector_adapter, chroma_adapter}.py` — Vector abstraction
5. ✅ `database/{models, session, init}.py` — ORM + DB
6. ✅ `repositories/*.py` — Data access layer
7. ✅ Agent implementations (can parallelize after base)
8. ✅ `orchestrator.py` — Phase coordination
9. ✅ `agent_factory.py` — Dependency injection
10. ✅ Route handlers — API endpoints

### Phase 2: Extension Foundation (Order Less Critical)
11. ✅ `extension/package.json` + `extension.ts` — Manifest + activation
12. ✅ `api/apiClient.ts` — Backend communication
13. ✅ `state/{runCache, stateManager}.ts` — Local state
14. ✅ `panelManager.ts` — Panel orchestration
15. ✅ Panel implementations + HTML templates (can parallelize)
16. ✅ `utils/{logger, validators}.ts` — Utilities

---

## Verification & Testing Strategy

### Unit Tests

**Backend Agent Tests**
- Mock Anthropic API calls (use responses library or pytest-mock)
- Test IngestionAgent: Parse sample story, verify extracted requirements
- Test DomainClassificationAgent: Classify various domain inputs
- Test RankingAgent: Verify scoring logic, boundary conditions
- Test GenerationAgent: Verify conditional execution (only if score ≥ threshold)

**Repository Tests**
- SQLite in-memory DB for fast testing
- CRUD operations per repository
- Audit log creation and retrieval

**API Client Tests (Extension)**
- Mock HTTP responses (jest mock or similar)
- Verify retry logic (success on retry, give up after N attempts)
- Verify error mapping (API error → user-friendly message)

### Integration Tests

**Backend Phase Flow**
- Full run: Story → Ingestion → Classification → Embedding → Retrieval → Coverage → Ranking → Audit
- Validate all phase outputs match response schemas
- Verify database records created for each phase
- Verify ChromaDB collection created and vectors stored

**Approval Gate Workflow**
- Submit story, ingestion runs
- Verify PhaseExecution + ApprovalGate created
- Submit rejection with feedback; verify status updated
- Submit approval; verify status updated and ready for next phase

**Generation Conditional**
- Run complete flow with ranking score 0.6 (< threshold) → verify Generation endpoint returns 403 Forbidden
- Run complete flow with ranking score 0.8 (≥ threshold) → verify Generation endpoint succeeds

**Error Handling**
- Agent times out → system records error, pauses
- Agent returns invalid output → system records error, pauses
- API error (rate limit, temporary outage) → client retries, then pauses if persistent

**ChromaDB Persistence**
- Embedding phase stores vectors in collection "run-{run_id}"
- Retrieval phase queries same collection
- Verify vector metadata recorded in SQLite
- Verify multiple runs maintain separate collections

### Manual E2E Tests (Smoke Test Checklist)
- [ ] Backend starts: `python -m uvicorn backend.app:app --reload`
- [ ] Database initialized: SQLite tables created
- [ ] ChromaDB running (or embedded mode if configured)
- [ ] `/health` endpoint returns 200 OK
- [ ] Extension loads in VS Code; all 5 panels render
- [ ] Story Input panel: textarea focused, ready for input
- [ ] Submit story via Story Input panel → Ingestion executes, output appears
- [ ] Approval panel shows ingestion output; click "Approve"
- [ ] Classification phase auto-runs; continues through Retrieval → Coverage → Ranking
- [ ] Ranking panel displays ranked items and score
- [ ] If ranking score ≥ 0.7: Generation panel visible
- [ ] If ranking score < 0.7: Generation panel hidden
- [ ] Click "Approve" on Ranking phase → Audit executes
- [ ] Run completed; run appears in cache
- [ ] Switch to previous run in extension → state restored (panels show cached data)
- [ ] Inspect SQLite: Run + PhaseExecution + ApprovalGate records for each phase
- [ ] Inspect audit logs: Full traceability of inputs, outputs, vector scores, conditioning

---

## Key Design Decisions

| Decision | Rationale | Alternative Considered |
|----------|-----------|----------------------|
| **Stateless API** | No session complexity; client manages context | Stateful orchestrator (session mgmt overhead) |
| **Separate phase endpoints** | Explicit, testable, allows partial retries | Single monolithic endpoint (less granular control) |
| **Manual approval gates** | Human control over risky decisions | Automatic with override (more automation, less control) |
| **Stateless clients** | Simpler extension, full audit trail | Local state management (risk of desync) |
| **Anthropic Claude** | High-quality reasoning for complex tasks | OpenAI GPT (equivalent, different pricing) |
| **ChromaDB persistence** | Reuse embeddings, cost savings | Re-embed each run (redundant computation) |
| **Ranking threshold for Generation** | Explicit gating on confidence | Always generate (less control) |

---

## Assumptions & Constraints

### Assumptions
- Anthropic API key available in environment (or passed in config)
- SQLite suffices for metadata (not high-concurrency production)
- ChromaDB runs locally (embedded mode or local server)
- VS Code Extension runs on same machine as FastAPI (localhost:8000)
- Stories are modestly sized (fit in HTTP request body, < 100KB)
- No large binary attachments (images, videos)
- Human approvers available within reasonable time (no infinite waits)

### Constraints & Rough Estimates
- **Agent execution timeout**: 5 minutes per agent (configurable)
- **Approval gate timeout**: 24 hours (auto-reject if no decision)
- **Generation score threshold**: 0.7 (configurable)
- **Run history cache size**: Recent 20 runs in extension memory
- **SQLite growth**: ~1-10 KB per run (metadata + audit logs); 1000 runs ≈ 10 MB
- **ChromaDB size**: Depends on embedding dimensionality; ~1 KB per vector (1000 vectors ≈ 1 MB)

---

## Further Refinements & Open Questions

1. **Timeout Implementation**
   - Q: How to enforce agent timeouts? (async tasks with timeout, separate worker thread, etc.)
   - Recommendation: Use asyncio.wait_for() if agents are async; else threading.Timer()

2. **Ranking Score Threshold Finalization**
   - Q: Confirm numeric threshold value (0.5, 0.7, 0.9)?
   - Recommendation: Start with 0.7; allow config in config.py + env override

3. **Auto-Retry Strategy for Failures**
   - Q: Retry 429/500/503 vs all errors?
   - Recommendation: Retry transient (429/500/503) 3× with backoff; fail immediately on 401/403/409

4. **Data Cleanup & Retention**
   - Q: How long to keep old runs in SQLite? (auto-archive, soft-delete, etc.)
   - Recommendation: Implement optional cleanup script; default keep last 1000 runs; soft-delete (preserve audit trail)

5. **Multi-User / Concurrent Runs**
   - Q: Should system support multiple concurrent runs, or one-at-a-time?
   - Note: Current plan assumes single user; concurrent runs need queue/session tracking

6. **Generation Output Actions**
   - Q: Can human edit generated code in panel, then save back to DB?
   - Recommendation: Yes; add `PUT /runs/{run_id}/generation` endpoint to persist edits

7. **Sensitive Data in Audit Logs**
   - Q: Should story text be logged? (PII concerns)
   - Recommendation: Log story text but add optional redaction; store in DB with encryption at rest if needed

---

## Summary for Next Steps

**Implementation Ready:**
- All backend classes and database models defined
- All extension panel structures defined
- API contracts fully specified (Pydantic schemas)
- Orchestration flow clear (stateless, separate phase endpoints)
- Error handling strategy defined (pause + human decision)

**Configuration Needed:**
- Confirm Ranking score threshold value
- Confirm agent timeout duration
- Confirm approval gate timeout
- Confirm data retention policy

**Development Ready:**
- Project structure can be scaffolded immediately
- Priority: API + DB layer first (agents can use mocks for testing)
- Phase 2: Extension frontend (assumes working backend)
- Integration testing: Full phase flow with real Anthropic API
