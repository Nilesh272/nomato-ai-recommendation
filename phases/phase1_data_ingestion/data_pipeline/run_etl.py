from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

from phases.phase1_data_ingestion.data_pipeline.clean import to_canonical
from phases.phase1_data_ingestion.data_pipeline.config import PipelineConfig
from phases.phase1_data_ingestion.data_pipeline.ingest import load_raw_dataset
from phases.phase1_data_ingestion.data_pipeline.load import (
    finish_run,
    get_connection,
    initialize_schema,
    replace_restaurants,
    start_run,
)
from phases.phase1_data_ingestion.data_pipeline.validate import validate_canonical


def _write_quality_report(run_id: str, payload: dict) -> None:
    reports_dir = Path("phases/phase1_data_ingestion/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / f"{run_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_pipeline(config: PipelineConfig) -> dict:
    run_id = str(uuid.uuid4())
    conn = get_connection(config.db_path)
    initialize_schema(conn)
    start_run(conn, run_id=run_id, source_dataset=config.dataset_name, source_split=config.dataset_split)

    try:
        raw, meta = load_raw_dataset(config.dataset_name, config.dataset_split)
        conn.execute(
            "UPDATE etl_runs SET source_fingerprint = ? WHERE run_id = ?",
            (meta.fingerprint, run_id),
        )
        conn.commit()
        canonical = to_canonical(raw)
        valid_df, report = validate_canonical(canonical)

        if config.reject_invalid_rows and report.valid_rows == 0:
            raise RuntimeError("Validation rejected all rows; nothing to load.")

        replace_restaurants(
            conn=conn,
            df=valid_df,
            source_dataset=config.dataset_name,
            source_split=config.dataset_split,
        )
        finish_run(
            conn=conn,
            run_id=run_id,
            status="success",
            total_rows=report.total_rows,
            valid_rows=report.valid_rows,
            report=report,
        )
        result = {"run_id": run_id, "status": "success", "report": report.__dict__, "source_fingerprint": meta.fingerprint}
        _write_quality_report(run_id, result)
        return result
    except Exception as exc:
        finish_run(
            conn=conn,
            run_id=run_id,
            status="failed",
            total_rows=0,
            valid_rows=0,
            report={"error": "pipeline_failed"},
            error_message=str(exc),
        )
        _write_quality_report(run_id, {"run_id": run_id, "status": "failed", "error": str(exc)})
        raise
    finally:
        conn.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 1 Zomato ETL.")
    parser.add_argument("--dataset-name", default=PipelineConfig.dataset_name)
    parser.add_argument("--split", default=PipelineConfig.dataset_split)
    parser.add_argument("--db-path", default=str(PipelineConfig.db_path))
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    config = PipelineConfig(
        dataset_name=args.dataset_name,
        dataset_split=args.split,
        db_path=Path(args.db_path),
    )
    result = run_pipeline(config)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

