"""
Phase 7: 事後検定力分析（Post-hoc Power Analysis）

【目的】
  N=47 という小サンプルでの統計的検定力を定量化し、
  Manuscript の Limitations に記載する数値を算出する。

【手法】
  非心 F 分布 (scipy.stats.ncf) を用いた OLS 線形回帰の検定力計算
  Effect size: Cohen's f² = R² / (1 - R²)

【出力ファイル】
  results/power_analysis_results.txt : 検定力分析レポート（Manuscript 引用用数値）
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.ndb_library.logger import setup_logger

logger = setup_logger(
    "perioperative_power_analysis",
    log_file=str(PROJECT_DIR / "03_Analysis" / "logs" / "07_power_analysis.log"),
)

# =========================================================================
# パラメータ（regression_results.csv から）
# =========================================================================
N_OBS    = 47      # 都道府県数（固定）
K_MODEL1 = 1       # Model 1: cancer_surgery_rate のみ
K_MODEL2 = 4       # Model 2: cancer_surgery_rate + aging_rate + income_per_capita + pop_density
ALPHA    = 0.05

R2_MODEL1 = 0.0089   # Unadjusted R²
R2_MODEL2 = 0.1967   # Adjusted R² (Model 2)

# Cohen の慣例的効果量
F2_SMALL  = 0.02
F2_MEDIUM = 0.15
F2_LARGE  = 0.35


def power_ols(r2: float, n: int, k: int, alpha: float = 0.05) -> float:
    """
    OLS 線形回帰の検定力を非心 F 分布で計算。

    Parameters
    ----------
    r2    : R²（決定係数）
    n     : サンプルサイズ
    k     : 予測変数の数（定数項を除く）
    alpha : 有意水準

    Returns
    -------
    power : float (0 ~ 1)
    """
    f2 = r2 / (1.0 - r2) if r2 < 1.0 else float("inf")
    df1 = k
    df2 = n - k - 1
    ncp = f2 * n
    if df2 <= 0:
        return float("nan")
    f_crit = stats.f.ppf(1.0 - alpha, df1, df2)
    power = 1.0 - stats.ncf.cdf(f_crit, df1, df2, ncp)
    return float(power)


def n_for_power(f2: float, k: int, target_power: float = 0.80, alpha: float = 0.05) -> int:
    """
    目標検定力を達成するために必要な最小 N を探索。

    Returns
    -------
    n_needed : int
    """
    for n in range(k + 2, 500):
        p = power_ols(f2 / (1.0 + f2), n, k, alpha)  # f² から R² に変換
        if p >= target_power:
            return n
    return 999  # 上限超え


def main() -> None:
    results_dir = PROJECT_DIR / "03_Analysis" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    lines = []

    def log_and_append(msg: str) -> None:
        logger.info(msg)
        lines.append(msg)

    log_and_append("=" * 65)
    log_and_append("Post-hoc Power Analysis: Perioperative Oral Care Study")
    log_and_append("=" * 65)
    log_and_append(f"N = {N_OBS} prefectures, alpha = {ALPHA}")
    log_and_append("")

    # -------------------------------------------------------------------------
    # 1. 観察 R² に基づく事後検定力
    # -------------------------------------------------------------------------
    log_and_append("--- Observed R² Based Power ---")
    for label, r2, k in [
        ("Model 1 (Unadjusted, k=1)", R2_MODEL1, K_MODEL1),
        ("Model 2 (Adjusted,   k=4)", R2_MODEL2, K_MODEL2),
    ]:
        f2 = r2 / (1.0 - r2)
        power = power_ols(r2, N_OBS, k, ALPHA)
        log_and_append(f"  {label}")
        log_and_append(f"    R² = {r2:.4f}, Cohen's f² = {f2:.4f}")
        log_and_append(f"    Post-hoc power = {power * 100:.1f}%")
        log_and_append("")

    # -------------------------------------------------------------------------
    # 2. 各効果量での検定力（N=47）
    # -------------------------------------------------------------------------
    log_and_append("--- Power by Effect Size at N=47, k=4 (Model 2) ---")
    for label, f2 in [("Small (f²=0.02)", F2_SMALL),
                       ("Medium (f²=0.15)", F2_MEDIUM),
                       ("Large  (f²=0.35)", F2_LARGE)]:
        r2_equiv = f2 / (1.0 + f2)
        power = power_ols(r2_equiv, N_OBS, K_MODEL2, ALPHA)
        log_and_append(f"  {label}: power = {power * 100:.1f}%")
    log_and_append("")

    # -------------------------------------------------------------------------
    # 3. 目標検定力 80% 達成に必要な N
    # -------------------------------------------------------------------------
    log_and_append("--- N Required for 80% Power (k=4) ---")
    for label, f2 in [("Small (f²=0.02)", F2_SMALL),
                       ("Medium (f²=0.15)", F2_MEDIUM),
                       ("Large  (f²=0.35)", F2_LARGE)]:
        n_needed = n_for_power(f2, K_MODEL2, target_power=0.80, alpha=ALPHA)
        note = " [exceeds 47 prefectures]" if n_needed > 47 else ""
        log_and_append(f"  {label}: N needed = {n_needed}{note}")
    log_and_append("")

    # -------------------------------------------------------------------------
    # 4. Manuscript Limitations への記載文（英語）
    # -------------------------------------------------------------------------
    f2_m2 = R2_MODEL2 / (1.0 - R2_MODEL2)
    power_m2 = power_ols(R2_MODEL2, N_OBS, K_MODEL2, ALPHA)
    n_medium = n_for_power(F2_MEDIUM, K_MODEL2, target_power=0.80)
    power_m1 = power_ols(R2_MODEL1, N_OBS, K_MODEL1, ALPHA)

    manuscript_text = f"""--- Manuscript Limitations (suggested text) ---

Post-hoc power analysis using a non-central F distribution
(alpha = {ALPHA}) indicated that with N = {N_OBS} prefectures and k = {K_MODEL2} predictors,
the adjusted model (R2 = {R2_MODEL2:.3f}; Cohen's f2 = {f2_m2:.3f}) achieved
approximately {power_m2 * 100:.0f}% power — below the conventional 80% threshold.
For a medium effect size (f2 = {F2_MEDIUM}), approximately N = {n_medium}
administrative units would be required to achieve 80% power,
which exceeds Japan's fixed unit of 47 prefectures.
Accordingly, the null finding should be interpreted as absence of
a detectable association at this ecological resolution rather than
proof of no association; Type II error cannot be excluded.
"""
    log_and_append(manuscript_text)
    log_and_append("=" * 65)

    # テキストファイルに保存
    out_path = results_dir / "power_analysis_results.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"検定力分析結果保存: {out_path}")


if __name__ == "__main__":
    main()
