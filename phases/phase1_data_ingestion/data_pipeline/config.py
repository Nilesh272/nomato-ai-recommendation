from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    dataset_name: str = "ManikaSaini/zomato-restaurant-recommendation"
    dataset_split: str = "train"
    db_path: Path = Path("phases/phase1_data_ingestion/data_pipeline/zomato.db")
    reject_invalid_rows: bool = True

