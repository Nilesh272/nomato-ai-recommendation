from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd
from datasets import DatasetDict, load_dataset


@dataclass(frozen=True)
class DatasetMeta:
    dataset_name: str
    split: str
    fingerprint: str | None


def load_raw_dataset(dataset_name: str, split: str = "train") -> tuple[pd.DataFrame, DatasetMeta]:
    """Load source dataset from Hugging Face into a pandas DataFrame plus basic version metadata."""
    data: DatasetDict | Any = load_dataset(dataset_name)
    if split not in data:
        available = ", ".join(data.keys()) if hasattr(data, "keys") else "unknown"
        raise ValueError(f"Split '{split}' not found. Available splits: {available}")

    ds = data[split]
    fingerprint = getattr(ds, "_fingerprint", None)
    return ds.to_pandas(), DatasetMeta(dataset_name=dataset_name, split=split, fingerprint=fingerprint)

