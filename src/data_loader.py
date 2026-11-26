"""Loading of the NSL-KDD files with correct headers and target columns."""
from pathlib import Path

import pandas as pd

from constants import ALL_COLUMNS, ATTACK_CATEGORY, FEATURE_COLUMNS


def load_nsl_kdd(path) -> pd.DataFrame:
    """Load a raw NSL-KDD file.

    The files have NO header row, so header=None is required (otherwise the
    first record is silently used as column names and one sample is lost).
    Adds two target columns: 'binary' (0 normal / 1 attack) and 'category'
    (Normal, DoS, Probe, R2L, U2R).
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found: {path}")

    df = pd.read_csv(path, header=None, names=ALL_COLUMNS)
    df["label"] = df["label"].str.strip().str.lower()

    unknown = sorted(set(df["label"]) - set(ATTACK_CATEGORY))
    if unknown:
        raise ValueError(f"Labels missing from ATTACK_CATEGORY: {unknown}")

    df["binary"] = (df["label"] != "normal").astype(int)
    df["category"] = df["label"].map(ATTACK_CATEGORY)
    return df


def split_xy(df: pd.DataFrame, target: str):
    """Return (X, y). 'difficulty' and every label column are excluded from X."""
    if target not in ("binary", "category"):
        raise ValueError("target must be 'binary' or 'category'")
    return df[FEATURE_COLUMNS].copy(), df[target].copy()