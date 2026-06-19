"""
Script 04: Descriptive statistics for all 47 prefectures

Computes mean, SD, min, max, and coefficient of variation for analysis
variables. Exports summary tables with English prefecture labels.

Outputs:
  03_Analysis/results/tables/ranking_implementation_rate.csv
  03_Analysis/results/tables/table1_descriptive.csv
  03_Analysis/results/tables/correlation_matrix.csv

---

スクリプト 04: 記述統計

47 都道府県の主要変数について記述統計量を算出し、表として出力する。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
_ANALYSIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(_ANALYSIS_DIR))

from prefecture_labels_en import prefecture_label_en
from src.ndb_library.logger import setup_logger

logger = setup_logger(
    "perioperative_descriptive",
    log_file=str(PROJECT_DIR / "03_Analysis" / "logs" / "04_descriptive_stats.log"),
)


def main() -> None:
    with open(PROJECT_DIR / "config" / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    data_path = PROJECT_DIR / cfg["output_paths"]["interim"] / cfg["output_paths"]["files"]["analysis_dataset"]
    tables_dir = PROJECT_DIR / cfg["output_paths"]["tables"]
    tables_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, encoding="utf-8-sig")

    # Ranking table (sorted by dental_mgmt_rate); add English prefecture labels for manuscripts
    rank_df = df.sort_values("dental_mgmt_rate", ascending=False).copy()
    if "都道府県" in rank_df.columns:
        rank_df["prefecture_en"] = rank_df["都道府県"].astype(str).apply(prefecture_label_en)
    rank_df.to_csv(tables_dir / "ranking_implementation_rate.csv", index=False, encoding="utf-8-sig")

    # Table 1: descriptive statistics (English column names for manuscript tables)
    stat_cols = [c for c in [
        "dental_mgmt_rate", "cancer_surgery_rate",
        "aging_rate", "income_per_capita", "pop_density", "physicians_per_100k",
        "主要がん手術総数", "周術期口腔機能管理料総数",
    ] if c in df.columns]
    _rename_export = {
        "主要がん手術総数": "major_cancer_surgery_claims_total",
        "周術期口腔機能管理料総数": "pofm_claims_total_B001_2_3",
    }
    df[stat_cols].rename(columns=_rename_export).describe().to_csv(
        tables_dir / "table1_descriptive.csv", encoding="utf-8-sig"
    )

    # 相関行列
    corr_cols = [c for c in [
        "dental_mgmt_rate", "cancer_surgery_rate",
        "aging_rate", "income_per_capita", "pop_density",
    ] if c in df.columns and df[c].notna().any()]
    if len(corr_cols) >= 2:
        df[corr_cols].corr(numeric_only=True).to_csv(tables_dir / "correlation_matrix.csv", encoding="utf-8-sig")

    logger.info(f"dental_mgmt_rate 記述統計: mean={df['dental_mgmt_rate'].mean():.1f}, "
                f"min={df['dental_mgmt_rate'].min():.1f}, max={df['dental_mgmt_rate'].max():.1f}")
    logger.info(f"cancer_surgery_rate 記述統計: mean={df['cancer_surgery_rate'].mean():.2f}, "
                f"min={df['cancer_surgery_rate'].min():.2f}, max={df['cancer_surgery_rate'].max():.2f}")
    logger.info(f"記述統計出力: {tables_dir}")


if __name__ == "__main__":
    main()

