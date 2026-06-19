"""
Script 03: Integrate external covariates and compute per-100,000 rates

Primary outcome: dental_mgmt_rate (B001-2/3 claims per 100,000 population)
Exposure: cancer_surgery_rate (16 cancer surgery K-codes per 100,000)

Covariates: aging rate, per-capita income, population density,
physicians per 100,000 (sensitivity), dentists per 100,000 (from script 08).

Output:
  02_Data/interim/analysis_dataset.csv

---

スクリプト 03: 外部統計の統合・人口補正率の計算

主要アウトカム dental_mgmt_rate、曝露 cancer_surgery_rate を算出し、
共変量を統合して解析用データセットを作成する。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.ndb_library.logger import setup_logger

logger = setup_logger(
    "perioperative_integrate",
    log_file=str(PROJECT_DIR / "03_Analysis" / "logs" / "03_integrate_covariates.log"),
)


def main() -> None:
    with open(PROJECT_DIR / "config" / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    results_dir = PROJECT_DIR / cfg["output_paths"]["results"]
    interim_dir = PROJECT_DIR / cfg["output_paths"]["interim"]
    out_file = interim_dir / cfg["output_paths"]["files"]["analysis_dataset"]
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. NDB 算定回数データ（Phase 2 出力）
    # -------------------------------------------------------------------------
    impl_path = results_dir / cfg["output_paths"]["files"]["implementation_rate"]
    if not impl_path.exists():
        raise FileNotFoundError("先に 02_calculate_implementation_rate.py を実行してください。")
    impl = pd.read_csv(impl_path, encoding="utf-8-sig")
    impl["pref_code"] = impl["pref_code"].astype(str).str.zfill(2)
    logger.info(f"算定回数データ読み込み: {len(impl)} 都道府県")

    # -------------------------------------------------------------------------
    # 2. 人口データ（NDB_XXX_dental_systemic から流用）
    # -------------------------------------------------------------------------
    pop_src = REPO_ROOT / "projects" / "NDB_XXX_dental_systemic" / "02_Data" / "interim" / "dental_disease_prefecture.csv"
    pop_df = pd.read_csv(pop_src, encoding="utf-8-sig")[["prefecture", "population"]].rename(
        columns={"prefecture": "都道府県", "population": "population"}
    )
    logger.info(f"人口データ読み込み: {len(pop_df)} 都道府県（dental_systemic から）")

    # -------------------------------------------------------------------------
    # 3. 共変量（NDB_XXX_dental_systemic から流用）
    # -------------------------------------------------------------------------
    cov_src = REPO_ROOT / "projects" / "NDB_XXX_dental_systemic" / "02_Data" / "interim" / "analysis_dataset_v2.csv"
    cov_df = pd.read_csv(cov_src, encoding="utf-8-sig")[["prefecture", "aging_rate", "income_per_capita", "pop_density"]].rename(
        columns={"prefecture": "都道府県"}
    )
    logger.info(f"共変量（aging_rate, income_per_capita, pop_density）読み込み: dental_systemic から")

    # -------------------------------------------------------------------------
    # 4. 追加共変量（NDB_XXX_temperature_emergency から流用）
    # -------------------------------------------------------------------------
    temp_src = REPO_ROOT / "projects" / "NDB_XXX_temperature_emergency" / "data" / "interim" / "03_covariates.csv"
    temp_df = pd.read_csv(temp_src, encoding="utf-8-sig")[["prefecture", "physicians_per_100k"]].rename(
        columns={"prefecture": "都道府県"}
    )
    logger.info(f"追加共変量（physicians_per_100k）読み込み: temperature_emergency から")

    # -------------------------------------------------------------------------
    # 4b. 歯科医師密度（08_dentist_data.py 出力）
    # -------------------------------------------------------------------------
    dentist_path = PROJECT_DIR / "02_Data" / "master" / "dentist_statistics_2022.csv"
    if dentist_path.exists():
        dentist_df = pd.read_csv(dentist_path, encoding="utf-8-sig")
        dentist_df["pref_code"] = dentist_df["pref_code"].astype(str).str.zfill(2)
        has_dentist = (
            "dentists_per_100k" in dentist_df.columns
            and dentist_df["dentists_per_100k"].notna().any()
        )
        if has_dentist:
            logger.info(f"歯科医師密度読み込み: {len(dentist_df)} 都道府県")
        else:
            dentist_df = None
            logger.warning("dentist_statistics_2022.csv が存在しますが dentists_per_100k が空です。"
                           "先に 08_dentist_data.py を実行してください。")
    else:
        dentist_df = None
        logger.warning("dentist_statistics_2022.csv が存在しません。"
                       "先に 08_dentist_data.py を実行してください。")

    # -------------------------------------------------------------------------
    # 5. データ統合
    # -------------------------------------------------------------------------
    merged = (
        impl
        .merge(pop_df, on="都道府県", how="left")
        .merge(cov_df, on="都道府県", how="left")
        .merge(temp_df, on="都道府県", how="left")
    )
    if dentist_df is not None:
        merged = merged.merge(dentist_df[["pref_code", "dentists_per_100k"]], on="pref_code", how="left")
        missing_d = merged["dentists_per_100k"].isna().sum()
        if missing_d > 0:
            logger.warning(f"歯科医師密度欠損: {missing_d} 都道府県")
        else:
            logger.info("dentists_per_100k 統合完了（欠損なし）")

    # -------------------------------------------------------------------------
    # 6. 人口10万人補正率の計算（主要アウトカム・曝露変数）
    # -------------------------------------------------------------------------
    PER = cfg["analysis_parameters"]["per_population"]  # 100,000
    pop = merged["population"].replace(0, pd.NA)
    merged["dental_mgmt_rate"] = merged["周術期口腔機能管理料総数"] / pop * PER
    merged["cancer_surgery_rate"] = merged["主要がん手術総数"] / pop * PER

    # -------------------------------------------------------------------------
    # 7. 検証ログ
    # -------------------------------------------------------------------------
    missing_pop = merged["population"].isna().sum()
    if missing_pop > 0:
        logger.warning(f"人口データ欠損: {missing_pop} 都道府県")
    logger.info(f"dental_mgmt_rate: min={merged['dental_mgmt_rate'].min():.1f}, "
                f"mean={merged['dental_mgmt_rate'].mean():.1f}, "
                f"max={merged['dental_mgmt_rate'].max():.1f} /10万人")
    logger.info(f"cancer_surgery_rate: min={merged['cancer_surgery_rate'].min():.2f}, "
                f"mean={merged['cancer_surgery_rate'].mean():.2f}, "
                f"max={merged['cancer_surgery_rate'].max():.2f} /10万人")

    # -------------------------------------------------------------------------
    # 8. 出力
    # -------------------------------------------------------------------------
    col_order = [
        "pref_code", "都道府県",
        "主要がん手術総数", "周術期口腔機能管理料総数",
        "dental_mgmt_rate", "cancer_surgery_rate",
        "population", "aging_rate", "income_per_capita", "pop_density",
        "physicians_per_100k", "dentists_per_100k",
        "raw_ratio",
    ]
    # 存在する列のみ選択
    col_order = [c for c in col_order if c in merged.columns]
    merged = merged[col_order]

    merged.to_csv(out_file, index=False, encoding="utf-8-sig")
    logger.info(f"analysis_dataset 保存: {out_file} ({len(merged)} 行 × {len(merged.columns)} 列)")


if __name__ == "__main__":
    main()
