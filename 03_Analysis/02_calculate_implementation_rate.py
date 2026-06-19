"""
Script 02: Merge medical and dental claim counts by prefecture

Merges Phase 1 outputs and computes raw implementation ratios
(dental management claims / major cancer surgery claims).

Population-adjusted rates (per 100,000) are computed in script 03.

Output:
  03_Analysis/results/implementation_rate_by_prefecture.csv

---

スクリプト 02: 算定回数の都道府県別統合

医科・歯科の算定回数を結合し、実施率（生の比率）を算出する。
人口10万人あたり指標はスクリプト 03 で計算する。
"""
from __future__ import annotations

import pandas as pd
import yaml

from _project_setup import PROJECT_DIR, setup_project_logger

logger = setup_project_logger(
    "perioperative_rate",
    PROJECT_DIR / "03_Analysis" / "logs" / "02_calculate_implementation_rate.log",
)


def main() -> None:
    cfg_path = PROJECT_DIR / "config" / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    interim_dir = PROJECT_DIR / cfg["output_paths"]["interim"]
    results_dir = PROJECT_DIR / cfg["output_paths"]["results"]
    tables_dir = PROJECT_DIR / cfg["output_paths"]["tables"]
    for d in [results_dir, tables_dir]:
        d.mkdir(parents=True, exist_ok=True)

    medical_path = interim_dir / cfg["output_paths"]["files"]["medical_surgery"]
    dental_path = interim_dir / cfg["output_paths"]["files"]["dental_management"]
    if not medical_path.exists() or not dental_path.exists():
        raise FileNotFoundError("先に 01_data_extraction.py を実行してください。")

    medical_df = pd.read_csv(medical_path, encoding="utf-8-sig")
    dental_df = pd.read_csv(dental_path, encoding="utf-8-sig")
    merged_df = pd.merge(medical_df, dental_df, on=["pref_code", "都道府県"], how="inner")

    # 生の比率（参考値。算定回数ベースのため100%超は正常）
    denom = merged_df["主要がん手術総数"].replace(0, pd.NA)
    merged_df["raw_ratio"] = (merged_df["周術期口腔機能管理料総数"] / denom) * 100
    merged_df["raw_ratio"] = merged_df["raw_ratio"].fillna(0.0)
    # 人口10万人補正率は Phase 3 (03_integrate_covariates.py) で算出
    merged_df = merged_df.sort_values("周術期口腔機能管理料総数", ascending=False).reset_index(drop=True)
    logger.info(f"医科手術合計: {merged_df['主要がん手術総数'].sum():,.0f} 件")
    logger.info(f"歯科管理料合計: {merged_df['周術期口腔機能管理料総数'].sum():,.0f} 件")

    out_csv = results_dir / cfg["output_paths"]["files"]["implementation_rate"]
    merged_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    merged_df.describe(include="all").to_csv(tables_dir / "implementation_rate_summary.csv", encoding="utf-8-sig")
    logger.info(f"算定回数データ出力: {out_csv}")


if __name__ == "__main__":
    main()
