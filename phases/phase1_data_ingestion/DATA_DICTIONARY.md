# Phase 1 Data Dictionary (Canonical Model)

This document describes the canonical schema produced by the Phase 1 ingestion pipeline and stored in SQLite table `restaurants`.

## Table: `restaurants`

- **restaurant_id**: Integer primary key (autoincrement). Stable identifier within a given ETL load.
- **name**: Restaurant name (required).
- **city**: City/location (required).
- **locality**: Area / locality / neighborhood (optional).
- **cuisines**: Normalized comma-separated cuisine tokens (optional). Example: `"North Indian, Chinese"`.
- **avg_cost_for_two**: Average cost for two (INR), numeric (optional).
- **rating**: Aggregate rating, numeric in \([0, 5]\) when present (optional).
- **votes**: Rating votes / review count (optional).
- **tags**: Free-text tags/features if available (optional).
- **source_dataset**: Hugging Face dataset name used for the load (required).
- **source_split**: Dataset split used for the load (required).
- **created_at**: Insert timestamp (UTC, SQLite `CURRENT_TIMESTAMP`).

## Table: `etl_runs`

- **run_id**: UUID for the ETL run (primary key).
- **source_dataset**: Dataset name requested for this run.
- **source_split**: Dataset split requested for this run.
- **source_fingerprint**: Split fingerprint provided by `datasets` (best-effort, may be null).
- **status**: `running` | `success` | `failed`.
- **total_rows**: Total raw rows processed after canonical mapping.
- **valid_rows**: Rows that passed validation and were loaded.
- **invalid_rows**: \(total_rows - valid_rows\).
- **quality_report_json**: JSON blob with validation counts.
- **error_message**: Populated for failed runs.
- **started_at** / **completed_at**: UTC timestamps for run bookkeeping.

## Quality report artifacts

Each ETL run writes a JSON artifact to `phases/phase1_data_ingestion/reports/<run_id>.json` containing the run status and validation report.

