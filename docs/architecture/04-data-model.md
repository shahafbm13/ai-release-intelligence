# Data Model

## PostgreSQL schema summary

### organizations
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| name | VARCHAR NOT NULL | |
| slug | VARCHAR UNIQUE NOT NULL | |
| created_at | TIMESTAMPTZ | |

### users
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| organization_id | UUID FK | |
| email | VARCHAR UNIQUE NOT NULL | |
| password_hash | VARCHAR NOT NULL | |
| role | VARCHAR NOT NULL | viewer, analyst, admin |
| created_at | TIMESTAMPTZ | |

### repositories
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| organization_id | UUID FK | |
| full_name | VARCHAR NOT NULL | org/repo |
| default_branch | VARCHAR | default main |
| created_at | TIMESTAMPTZ | |

**Index:** `(organization_id, full_name)` UNIQUE

### ci_runs
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| repository_id | UUID FK | |
| workflow_name | VARCHAR | |
| branch | VARCHAR | |
| commit_sha | VARCHAR(40) | |
| conclusion | VARCHAR | success, failure, etc. |
| status_url | TEXT | |
| processing_status | VARCHAR | enum |
| idempotency_key | VARCHAR UNIQUE NOT NULL | |
| ingested_at | TIMESTAMPTZ | |
| enqueued_at | TIMESTAMPTZ | |
| completed_at | TIMESTAMPTZ | |

**Indexes:** `(repository_id, ingested_at DESC)`, `(processing_status)`

### failure_occurrences
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| ci_run_id | UUID FK | |
| test_name | VARCHAR | |
| suite_name | VARCHAR | |
| error_type | VARCHAR | |
| error_message | TEXT | |
| stack_trace | TEXT | |
| log_excerpt | TEXT | masked |
| retry_number | INT DEFAULT 0 | |
| fingerprint | VARCHAR | normalized hash |
| created_at | TIMESTAMPTZ | |

**Indexes:** `(ci_run_id)`, `(fingerprint)`, `(repository_id via join)` for similarity queries

### classifications
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| failure_occurrence_id | UUID FK UNIQUE | one active per failure in MVP |
| category | VARCHAR | taxonomy |
| subcategory | VARCHAR | |
| suspected_component | VARCHAR | |
| summary | TEXT | |
| likely_cause | TEXT | |
| suggested_action | TEXT | |
| confidence | NUMERIC(4,3) | |
| evidence_refs | JSONB | |
| insufficient_information | BOOLEAN | |
| provider | VARCHAR | groq, gemini, rules |
| model | VARCHAR | |
| prompt_version | VARCHAR | |
| input_hash | VARCHAR | |
| input_tokens | INT | |
| output_tokens | INT | |
| duration_ms | INT | |
| trace_id | VARCHAR | |
| created_at | TIMESTAMPTZ | |

### similar_failure_links
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| failure_occurrence_id | UUID FK | |
| matched_failure_occurrence_id | UUID FK | |
| method | VARCHAR | exact_message, test_name, error_type |
| score | NUMERIC(4,3) | |

### release_assessments
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| ci_run_id | UUID FK UNIQUE | |
| risk_level | VARCHAR | |
| score | NUMERIC(5,2) | |
| factors_json | JSONB | |
| missing_info_json | JSONB | |
| recommendation | VARCHAR | proceed, caution, hold |
| explanation | TEXT | |
| created_at | TIMESTAMPTZ | |

### human_feedback
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| failure_occurrence_id | UUID FK | |
| classification_id | UUID FK | |
| action | VARCHAR | accept, correct |
| corrected_category | VARCHAR NULL | |
| corrected_component | VARCHAR NULL | |
| note | TEXT | |
| resolved | BOOLEAN | |
| cluster_id | UUID FK NULL | |
| created_at | TIMESTAMPTZ | |

### audit_events
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| organization_id | UUID FK | |
| actor_id | UUID FK NULL | |
| action | VARCHAR | |
| resource_type | VARCHAR | |
| resource_id | UUID | |
| correlation_id | VARCHAR | |
| metadata_json | JSONB | |
| created_at | TIMESTAMPTZ | |

### ingested_events
| Column | Type | Notes |
|--------|------|-------|
| id | UUID PK | |
| delivery_id | VARCHAR UNIQUE | |
| event_type | VARCHAR | |
| payload_json | JSONB | |
| correlation_id | VARCHAR | |
| created_at | TIMESTAMPTZ | |

## Indexing decisions

- **idempotency_key** UNIQUE on ci_runs — fast duplicate detection.
- **fingerprint** on failures — similar-failure candidate filtering.
- **ingested_at DESC** on ci_runs — dashboard list performance.
- JSONB on factors/evidence — flexible schema; GIN index deferred until query patterns proven.

## Migration strategy

- Alembic revision per milestone schema change.
- Seed script separate from migrations.

## pgvector

**Not in MVP.** Revisit when baseline retrieval metrics collected. See ADR-005.
