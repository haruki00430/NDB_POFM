"""
Script 03: Integrate external covariates and compute per-100,000 rates

Primary outcome: dental_mgmt_rate (B001-2/3 claims per 100,000 population)
Exposure: cancer_surgery_rate (16 cancer surgery K-codes per 100,000)

Covariates: aging rate, per-capita income, population density,
physicians per 100,000 (sensitivity), dentists per 100,000 (from script 08).

Master covariates are read from 02_Data/master/ (self-contained; no sibling
project paths required).

Output:
  02_Data/interim/analysis_dataset.csv

---

スクリプト 03: 外部統計の統合・人口補正率の計算

02_Data/master/ の都道府県マスターを用い、主要アウトカム・曝露・共変量を統合する。
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from _project_setup import PROJECT_DIR, setup_project_logger

logger = setup_project_logger(
    "perioperative_integrate",
    PROJECT_DIR / "03_Analysis" / "logs" / "03_integrate_covariates.log",
)


def _load_master_table(cfg: dict, key: str) -> pd.DataFrame:
    """Load a prefecture-level master CSV defined in config.external_statistics."""
    spec = cfg["external_statistics"][key]
    path = PROJECT_DIR / spec["path"]
    if not path.exists():
        raise FileNotFoundError(f"Master data not found: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    use_cols = spec.get("use_cols")
    if use_cols:
        missing = [c for c in use_cols if c not in df.columns]
        if missing:
            raise ValueError(f"{path.name} is missing columns: {missing}")
        df = df[use_cols].copy()
    pref_col = spec.get("prefecture_col", "prefecture")
    if pref_col in df.columns:
        df = df.rename(columns={pref_col: "都道府県"})
    if "pref_code" in df.columns:
        df["pref_code"] = df["pref_code"].astype(str).str.zfill(2)
    return df


def main() -> None:
    with open(PROJECT_DIR / "config" / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    results_dir = PROJECT_DIR / cfg["output_paths"]["results"]
    interim_dir = PROJECT_DIR / cfg["output_paths"]["interim"]
    out_file = interim_dir / cfg["output_paths"]["files"]["analysis_dataset"]
    out_file.parent.mkdir(parents=True, exist_ok=True)

    impl_path = results_dir / cfg["output_paths"]["files"]["implementation_rate"]
    if not impl_path.exists():
        raise FileNotFoundError("先に 02_calculate_implementation_rate.py を実行してください。")
    impl = pd.read_csv(impl_path, encoding="utf-8-sig")
    impl["pref_code"] = impl["pref_code"].astype(str).str.zfill(2)
    logger.info(f"算定回数データ読み込み: {len(impl)} 都道府県")

    demo_df = _load_master_table(cfg, "prefecture_demographics")
    logger.info(
        "都道府県マスター読み込み: "
        f"{len(demo_df)} 都道府県（02_Data/master/prefecture_demographics_covariates.csv）"
    )

    dentist_path = PROJECT_DIR / cfg["external_statistics"]["dentist_statistics"]["path"]
    dentist_df = None
    if dentist_path.exists():
        dentist_df = pd.read_csv(dentist_path, encoding="utf-8-sig")
        dentist_df["pref_code"] = dentist_df["pref_code"].astype(str).str.zfill(2)
        if (
            "dentists_per_100k" in dentist_df.columns
            and dentist_df["dentists_per_100k"].notna().any()
        ):
            logger.info(f"歯科医師密度読み込み: {len(dentist_df)} 都道府県")
        else:
            dentist_df = None
            logger.warning(
                "dentist_statistics_2022.csv が存在しますが dentists_per_100k が空です。"
                "先に 08_dentist_data.py を実行してください。"
            )
    else:
        logger.warning(
            "dentist_statistics_2022.csv が存在しません。"
            "先に 08_dentist_data.py を実行してください。"
        )

    merged = impl.merge(demo_df, on="都道府県", how="left")
    if dentist_df is not None:
        merged = merged.merge(
            dentist_df[["pref_code", "dentists_per_100k"]],
            on="pref_code",
            how="left",
            suffixes=("", "_dentist"),
        )
        missing_d = merged["dentists_per_100k"].isna().sum()
        if missing_d > 0:
            logger.warning(f"歯科医師密度欠損: {missing_d} 都道府県")
        else:
            logger.info("dentists_per_100k 統合完了（欠損なし）")

    per = cfg["analysis_parameters"]["per_population"]
    pop = merged["population"].replace(0, pd.NA)
    merged["dental_mgmt_rate"] = merged["周術期口腔機能管理料総数"] / pop * per
    merged["cancer_surgery_rate"] = merged["主要がん手術総数"] / pop * per

    missing_pop = merged["population"].isna().sum()
    if missing_pop > 0:
        logger.warning(f"人口データ欠損: {missing_pop} 都道府県")
    logger.info(
        f"dental_mgmt_rate: min={merged['dental_mgmt_rate'].min():.1f}, "
        f"mean={merged['dental_mgmt_rate'].mean():.1f}, "
        f"max={merged['dental_mgmt_rate'].max():.1f} /10万人"
    )
    logger.info(
        f"cancer_surgery_rate: min={merged['cancer_surgery_rate'].min():.2f}, "
        f"mean={merged['cancer_surgery_rate'].mean():.2f}, "
        f"max={merged['cancer_surgery_rate'].max():.2f} /10万人"
    )

    col_order = [
        "pref_code",
        "都道府県",
        "主要がん手術総数",
        "周術期口腔機能管理料総数",
        "dental_mgmt_rate",
        "cancer_surgery_rate",
        "population",
        "aging_rate",
        "income_per_capita",
        "pop_density",
        "physicians_per_100k",
        "dentists_per_100k",
        "raw_ratio",
    ]
    col_order = [c for c in col_order if c in merged.columns]
    merged = merged[col_order]

    merged.to_csv(out_file, index=False, encoding="utf-8-sig")
    logger.info(
        f"analysis_dataset 保存: {out_file} ({len(merged)} 行 × {len(merged.columns)} 列)"
    )


if __name__ == "__main__":
    main()
