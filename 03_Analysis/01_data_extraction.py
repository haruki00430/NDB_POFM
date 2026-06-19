"""
Script 01: NDB data extraction for perioperative oral care analysis

Extracts prefecture-level claim counts for major cancer surgery (16 K-codes)
and perioperative oral management fees (B001-2, B001-3) from NDB Open Data
No.10 Excel files and saves interim CSVs.

Uses the classification-code column (not the numeric procedure ID column).
Empty continuation rows are forward-filled and aggregated per config.

Outputs:
  02_Data/interim/perioperative_medical_surgery.csv
  02_Data/interim/perioperative_dental_management.csv

---

スクリプト 01: NDB データ抽出（周術期口腔ケア解析）

医科手術（K コード）と歯科管理料（B001-2/3）を都道府県別に抽出し、
interim へ保存する。分類コード列を用い、空の継続行は前方埋めして合算する。
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Hashable

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.ndb_library.logger import setup_logger

logger = setup_logger(
    "perioperative_extract",
    log_file=str(PROJECT_DIR / "03_Analysis" / "logs" / "01_data_extraction.log"),
)


def clean_numeric(value, masking_strategy: str) -> float:
    """NDBの数値列をクリーニングする。"""
    if pd.isna(value):
        return 0.0
    s = str(value).strip()
    if s in {"-", "－"}:
        return 5.0 if masking_strategy == "moderate" else 0.0
    s = s.translate(str.maketrans("０１２３４５６７８９", "0123456789"))
    s = s.replace(",", "").replace("，", "")
    try:
        return float(s)
    except ValueError:
        return 0.0


def read_config() -> Dict:
    cfg_path = PROJECT_DIR / "config" / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_classification_code_column(df: pd.DataFrame) -> Hashable:
    """
    NDB の「分類コード」列（MultiIndex）を特定する。
    「診療行為コード」（数値ID）列と取り違えない。
    """
    candidates = [c for c in df.columns if "分類" in str(c) and "コード" in str(c)]
    if candidates:
        return candidates[0]
    fallback = [c for c in df.columns if "コード" in str(c)]
    if not fallback:
        raise ValueError("コード列が見つかりません")
    logger.warning("分類コード列が見つからず、先頭のコード列を使用します: %s", fallback[0])
    return fallback[0]


def effective_classification_codes(series: pd.Series, aggregate_subrows: bool) -> pd.Series:
    """
    行ごとの有効分類コード。aggregate_subrows=True のとき、空行は直前のコードに帰属（前方埋め）。
    """
    filled = series.ffill() if aggregate_subrows else series
    out = pd.Series(pd.NA, index=series.index, dtype="string")
    valid = filled.notna()
    out.loc[valid] = filled[valid].astype(str).str.strip()
    return out


def extract_prefecture_counts(df: pd.DataFrame, filtered_df: pd.DataFrame, value_name: str, masking_strategy: str) -> pd.DataFrame:
    """都道府県列を走査し、対象コード行の合計を返す。"""
    pref_rows = []
    for col in df.columns:
        if not (isinstance(col, tuple) and len(col) == 2):
            continue
        level0, level1 = col
        if str(level0).isdigit() and len(str(level0)) == 2:
            pref_rows.append(
                {
                    "pref_code": str(level0).zfill(2),
                    "都道府県": str(level1),
                    value_name: filtered_df[col].apply(lambda x: clean_numeric(x, masking_strategy)).sum(),
                }
            )
    out = pd.DataFrame(pref_rows).sort_values("pref_code").reset_index(drop=True)
    return out


def main() -> None:
    logger.info("Phase1 データ抽出を開始")
    config = read_config()
    masking_strategy = config["analysis_parameters"]["masking_strategy"]

    med_path = REPO_ROOT / config["medical_surgery"]["data_path"]
    den_path = REPO_ROOT / config["dental_management"]["data_path"]
    if not med_path.exists():
        raise FileNotFoundError(f"医科データが見つかりません: {med_path}")
    if not den_path.exists():
        raise FileNotFoundError(f"歯科データが見つかりません: {den_path}")

    med_df = pd.read_excel(med_path, sheet_name=config["medical_surgery"]["sheet_name"], header=[2, 3])
    den_df = pd.read_excel(den_path, sheet_name=0, header=[2, 3])

    med_code_col = resolve_classification_code_column(med_df)
    den_code_col = resolve_classification_code_column(den_df)
    med_agg = bool(config["medical_surgery"].get("aggregate_classification_subrows", True))
    den_agg = bool(config["dental_management"].get("aggregate_classification_subrows", True))

    target_k = [x["code"] for x in config["medical_surgery"]["target_surgery_codes"]]
    target_b = [x["code"] for x in config["dental_management"]["target_codes"]]
    med_eff = effective_classification_codes(med_df[med_code_col], med_agg)
    den_eff = effective_classification_codes(den_df[den_code_col], den_agg)
    med_filtered = med_df.loc[med_eff.isin(target_k)].copy()
    den_filtered = den_df.loc[den_eff.isin(target_b)].copy()

    logger.info(
        "医科: 分類コード列=%s, aggregate_subrows=%s, 抽出行数=%s / 対象コード数=%s",
        med_code_col,
        med_agg,
        len(med_filtered),
        len(target_k),
    )
    logger.info(
        "歯科: 分類コード列=%s, aggregate_subrows=%s, 抽出行数=%s / 対象コード数=%s",
        den_code_col,
        den_agg,
        len(den_filtered),
        len(target_b),
    )

    med_out = extract_prefecture_counts(med_df, med_filtered, "主要がん手術総数", masking_strategy)
    den_out = extract_prefecture_counts(den_df, den_filtered, "周術期口腔機能管理料総数", masking_strategy)

    interim_dir = PROJECT_DIR / config["output_paths"]["interim"]
    interim_dir.mkdir(parents=True, exist_ok=True)
    med_out.to_csv(interim_dir / config["output_paths"]["files"]["medical_surgery"], index=False, encoding="utf-8-sig")
    den_out.to_csv(interim_dir / config["output_paths"]["files"]["dental_management"], index=False, encoding="utf-8-sig")
    logger.info(f"保存完了: {interim_dir}")


if __name__ == "__main__":
    main()

