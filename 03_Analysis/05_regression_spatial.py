"""
Script 05: OLS regression, sensitivity analysis, and spatial statistics

Outcome (Y): dental_mgmt_rate (POFM claims per 100,000)
Exposure (X): cancer_surgery_rate (major cancer surgery per 100,000)
Covariates: aging_rate, income_per_capita, pop_density

Analyses:
  - Model 1 (unadjusted) and Model 2 (adjusted) OLS with HC3 SE
  - Seven sensitivity specifications (baseline, HC3, outliers, metros,
    log-transform, physicians, dentists)
  - Global Moran's I, Lagrange Multiplier tests, Spatial Lag Model (SLM)

Outputs:
  regression_results.csv, sensitivity_results.csv, morans_i_results.txt,
  lm_test_results.csv, slm_results.csv, correlation_matrix.csv

---

スクリプト 05: 回帰・感度分析・空間統計

OLS 回帰（主モデル・感度分析 7 仕様）、Global Moran's I、
LM 検定、空間ラグモデル（SLM）を実行する。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml

from _project_setup import DATA_ROOT, PROJECT_DIR, setup_project_logger

logger = setup_project_logger(
    "perioperative_regression_spatial",
    PROJECT_DIR / "03_Analysis" / "logs" / "05_regression_spatial.log",
)

Y_COL = "dental_mgmt_rate"
X_MAIN = "cancer_surgery_rate"
COVARS = ["aging_rate", "income_per_capita", "pop_density"]
LARGE_CITY_CODES = ["13", "27", "23"]  # 東京・大阪・愛知


def _ols_row(label: str, df: pd.DataFrame, y_col: str, x_cols: list[str],
             cov_type: str = "HC3") -> dict:
    """OLS を実行して結果1行を返す。"""
    sub = df[[y_col] + x_cols].dropna()
    X = sm.add_constant(sub[x_cols])
    model = sm.OLS(sub[y_col], X).fit(cov_type=cov_type)
    ci = model.conf_int()
    return {
        "model": label,
        "n": len(sub),
        "r2": round(float(model.rsquared), 4),
        "adj_r2": round(float(model.rsquared_adj), 4),
        "x_main": x_cols[0],
        "coef": round(float(model.params[x_cols[0]]), 4),
        "se": round(float(model.bse[x_cols[0]]), 4),
        "t": round(float(model.tvalues[x_cols[0]]), 4),
        "p_value": round(float(model.pvalues[x_cols[0]]), 4),
        "ci_low": round(float(ci.loc[x_cols[0], 0]), 4),
        "ci_high": round(float(ci.loc[x_cols[0], 1]), 4),
        "aic": round(float(model.aic), 2),
        "cov_type": cov_type,
    }


def _cook_outlier_mask(df: pd.DataFrame, y_col: str, x_cols: list[str]) -> pd.Series:
    """Cook's distance > 4/n の行をマスク（True=外れ値）。"""
    sub = df[[y_col] + x_cols].dropna()
    X = sm.add_constant(sub[x_cols])
    infl = sm.OLS(sub[y_col], X).fit().get_influence()
    cooks_d = infl.cooks_distance[0]
    threshold = 4.0 / len(sub)
    mask = pd.Series(False, index=df.index)
    mask.loc[sub.index] = cooks_d > threshold
    return mask


def _run_lm_and_slm(df, gdf, w, x_adj, avail_covars, results_dir, logger) -> None:
    """
    LagrangeMultiplier 検定でモデル選択し、必要なら SLM / SEM を推定する。

    判定テーブル（Anselin 1988 決定規則）:
      LM-lag 有意 & LM-error 非有意  → SLM
      LM-lag 非有意 & LM-error 有意  → SEM
      両方有意                        → RLM で優位な方
      両方非有意                      → OLS で十分
    """
    try:
        from spreg import OLS as SPREG_OLS, ML_Lag, ML_Error

        # SLM 用サブデータ（全変数揃った行のみ）
        needed = [Y_COL] + x_adj
        sub = gdf[[c for c in needed if c in gdf.columns]].copy()
        # GDF インデックスを振り直し、欠損行を除外
        sub = sub.dropna(subset=needed).reset_index(drop=True)

        if len(sub) < 10:
            logger.warning(f"SLM: 有効サンプルが少なすぎます (n={len(sub)}), スキップ")
            return

        # 空間重み行列を有効行に合わせて再構築
        # （元の gdf からサブセットした行に対応する新しい Queen 重み行列）
        gdf_sub = gdf.loc[sub.index].copy().reset_index(drop=True)
        from libpysal.weights import Queen
        w_sub = Queen.from_dataframe(gdf_sub, use_index=False)
        w_sub.transform = "r"

        y_arr = sub[Y_COL].values.reshape(-1, 1)
        X_arr = sub[x_adj].values  # 定数項は spreg 内部で追加

        n_sp = len(sub)

        # --- Step 1: 空間診断付き OLS で LM 統計量取得 ---
        ols_sp = SPREG_OLS(
            y_arr, X_arr, w=w_sub,
            name_y=Y_COL, name_x=x_adj,
            spat_diag=True,
        )

        lm_lag_stat   = float(ols_sp.lm_lag[0])
        lm_lag_p      = float(ols_sp.lm_lag[1])
        lm_error_stat = float(ols_sp.lm_error[0])
        lm_error_p    = float(ols_sp.lm_error[1])
        rlm_lag_stat  = float(ols_sp.rlm_lag[0])
        rlm_lag_p     = float(ols_sp.rlm_lag[1])
        rlm_error_stat = float(ols_sp.rlm_error[0])
        rlm_error_p   = float(ols_sp.rlm_error[1])

        logger.info(
            f"LM検定: LM-lag={lm_lag_stat:.4f}(p={lm_lag_p:.4f}), "
            f"LM-error={lm_error_stat:.4f}(p={lm_error_p:.4f})"
        )
        logger.info(
            f"RLM検定: RLM-lag={rlm_lag_stat:.4f}(p={rlm_lag_p:.4f}), "
            f"RLM-error={rlm_error_stat:.4f}(p={rlm_error_p:.4f})"
        )

        # --- Step 2: モデル選択 ---
        ALPHA = 0.05
        if lm_lag_p < ALPHA and lm_error_p >= ALPHA:
            selected_model = "SLM"
        elif lm_lag_p >= ALPHA and lm_error_p < ALPHA:
            selected_model = "SEM"
        elif lm_lag_p < ALPHA and lm_error_p < ALPHA:
            selected_model = "SLM" if rlm_lag_p < rlm_error_p else "SEM"
        else:
            selected_model = "OLS_sufficient"

        logger.info(f"選択モデル: {selected_model}")

        # LM検定結果を CSV 保存
        lm_df = pd.DataFrame([{
            "n_spatial": n_sp,
            "lm_lag_stat": round(lm_lag_stat, 4),
            "lm_lag_p": round(lm_lag_p, 4),
            "lm_error_stat": round(lm_error_stat, 4),
            "lm_error_p": round(lm_error_p, 4),
            "rlm_lag_stat": round(rlm_lag_stat, 4),
            "rlm_lag_p": round(rlm_lag_p, 4),
            "rlm_error_stat": round(rlm_error_stat, 4),
            "rlm_error_p": round(rlm_error_p, 4),
            "selected_model": selected_model,
        }])
        lm_df.to_csv(results_dir / "lm_test_results.csv", index=False, encoding="utf-8-sig")
        logger.info(f"LM検定結果保存: {results_dir / 'lm_test_results.csv'}")

        # --- Step 3: SLM または SEM の推定 ---
        if selected_model == "OLS_sufficient":
            logger.info("LM検定が両方非有意 → OLS で十分、空間回帰モデルはスキップ")
            # OLS_sufficient の旨を slm_results.csv に記録
            pd.DataFrame([{"model": "OLS_sufficient", "note": "LM tests not significant; OLS is adequate"}]).to_csv(
                results_dir / "slm_results.csv", index=False, encoding="utf-8-sig"
            )
            return

        if selected_model == "SLM":
            sp_model = ML_Lag(y_arr, X_arr, w=w_sub, name_y=Y_COL, name_x=x_adj)
            rho_val = float(sp_model.rho)
            model_label = "SLM (Spatial Lag Model)"
        else:
            sp_model = ML_Error(y_arr, X_arr, w=w_sub, name_y=Y_COL, name_x=x_adj)
            rho_val = float(sp_model.lam)
            model_label = "SEM (Spatial Error Model)"

        sp_aic = float(sp_model.aic)
        sp_pr2 = float(sp_model.pr2)

        # 既存 OLS AIC（Model 2）を regression_results.csv から読む
        try:
            ols_aic = float(
                pd.read_csv(results_dir / "regression_results.csv")
                  .set_index("model")
                  .loc["Model2_Adjusted", "aic"]
            )
        except Exception:
            ols_aic = float("nan")
        delta_aic = sp_aic - ols_aic

        # spreg の betas: [const, x_adj[0], x_adj[1], ...]
        # z_stat: list of (z, p) tuples for each beta, then rho at the end (ML_Lag)
        betas = sp_model.betas.flatten()
        z_stats = sp_model.z_stat  # list of (z, p) tuples

        def _safe_zp(z_list, idx):
            try:
                return float(z_list[idx][0]), float(z_list[idx][1])
            except Exception:
                return float("nan"), float("nan")

        x_main_idx = 1  # betas[0]=const, betas[1]=cancer_surgery_rate
        x_main_coef = float(betas[x_main_idx]) if len(betas) > x_main_idx else float("nan")
        x_main_z, x_main_p = _safe_zp(z_stats, x_main_idx)

        # rho の z値・p値（ML_Lag では z_stat の最後の要素）
        rho_z, rho_p = _safe_zp(z_stats, -1)

        result_row = {
            "model": model_label,
            "n": n_sp,
            "spatial_param_label": "rho" if selected_model == "SLM" else "lambda",
            "spatial_param": round(rho_val, 4),
            "spatial_param_z": round(rho_z, 4),
            "spatial_param_p": round(rho_p, 4),
            f"{X_MAIN}_coef": round(x_main_coef, 4),
            f"{X_MAIN}_z": round(x_main_z, 4),
            f"{X_MAIN}_p": round(x_main_p, 4),
            "pseudo_r2": round(sp_pr2, 4),
            "log_likelihood": round(float(sp_model.logll), 4),
            "aic": round(sp_aic, 2),
            "ols_aic": round(ols_aic, 2),
            "delta_aic_vs_ols": round(delta_aic, 2),
        }
        pd.DataFrame([result_row]).to_csv(results_dir / "slm_results.csv", index=False, encoding="utf-8-sig")
        logger.info(
            f"{model_label}: rho={rho_val:.4f}(z={rho_z:.4f},p={rho_p:.4f}), "
            f"{X_MAIN} coef={x_main_coef:.4f} z={x_main_z:.4f} p={x_main_p:.4f}, "
            f"AIC={sp_aic:.2f} (ΔAIC vs OLS={delta_aic:.2f}), pseudo-R2={sp_pr2:.4f}"
        )

    except ImportError:
        logger.warning("spreg が未インストールのため LM検定/SLM をスキップ。`pip install spreg` を実行してください。")
    except Exception as e:
        logger.warning(f"LM検定/SLM 実行エラー: {e}")
        import traceback
        logger.warning(traceback.format_exc())


def main() -> None:
    with open(PROJECT_DIR / "config" / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    data_path = PROJECT_DIR / cfg["output_paths"]["interim"] / cfg["output_paths"]["files"]["analysis_dataset"]
    results_dir = PROJECT_DIR / cfg["output_paths"]["results"]
    results_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path, encoding="utf-8-sig")
    df["pref_code"] = df["pref_code"].astype(str).str.zfill(2)

    avail_covars = [c for c in COVARS if c in df.columns and df[c].notna().any()]
    logger.info(f"有効な共変量: {avail_covars}")
    logger.info(f"サンプルサイズ: {df.shape[0]} 都道府県")

    # =========================================================================
    # 主モデル（Model 1: Unadjusted / Model 2: Adjusted）
    # =========================================================================
    x_adj = [X_MAIN] + avail_covars  # スコープを main() レベルで定義

    rows = []
    rows.append(_ols_row("Model1_Unadjusted", df, Y_COL, [X_MAIN], cov_type="HC3"))
    if avail_covars:
        rows.append(_ols_row("Model2_Adjusted", df, Y_COL, x_adj, cov_type="HC3"))
    pd.DataFrame(rows).to_csv(results_dir / "regression_results.csv", index=False, encoding="utf-8-sig")
    for r in rows:
        logger.info(f"{r['model']}: n={r['n']}, R²={r['r2']}, coef={r['coef']}, p={r['p_value']}")

    # 全変数の係数を別ファイルに出力（Model 2）
    if avail_covars:
        sub = df[[Y_COL] + x_adj].dropna()
        X = sm.add_constant(sub[x_adj])
        m2 = sm.OLS(sub[Y_COL], X).fit(cov_type="HC3")
        ci = m2.conf_int()
        full_rows = []
        for var in x_adj:
            full_rows.append({
                "variable": var, "coef": round(float(m2.params[var]), 4),
                "se": round(float(m2.bse[var]), 4),
                "t": round(float(m2.tvalues[var]), 4),
                "p_value": round(float(m2.pvalues[var]), 4),
                "ci_low": round(float(ci.loc[var, 0]), 4),
                "ci_high": round(float(ci.loc[var, 1]), 4),
            })
        pd.DataFrame(full_rows).to_csv(results_dir / "model2_full_coefficients.csv", index=False, encoding="utf-8-sig")
        for r in full_rows:
            logger.info(f"  {r['variable']}: coef={r['coef']}, p={r['p_value']}")

    # =========================================================================
    # 感度分析 6仕様
    # =========================================================================
    x_adj = [X_MAIN] + avail_covars
    sens_rows = []

    # Spec 1: Baseline OLS（通常SE）
    sens_rows.append(_ols_row("Spec1_Baseline_OLS", df, Y_COL, x_adj, cov_type="nonrobust"))

    # Spec 2: HC3 robust SE（主解析と同じ）
    sens_rows.append(_ols_row("Spec2_HC3_Robust", df, Y_COL, x_adj, cov_type="HC3"))

    # Spec 3: 外れ値除外（Cook's distance > 4/n）
    outlier_mask = _cook_outlier_mask(df, Y_COL, x_adj)
    n_out = outlier_mask.sum()
    logger.info(f"外れ値除外: {n_out} 都道府県 (Cook's D > 4/{len(df)})")
    sens_rows.append(_ols_row(f"Spec3_No_Outliers(n={len(df)-n_out})", df[~outlier_mask], Y_COL, x_adj, cov_type="HC3"))

    # Spec 4: 大都市除外（東京・大阪・愛知）
    city_mask = df["pref_code"].isin(LARGE_CITY_CODES)
    df_no_city = df[~city_mask]
    sens_rows.append(_ols_row(f"Spec4_No_LargeCities(n={len(df_no_city)})", df_no_city, Y_COL, x_adj, cov_type="HC3"))

    # Spec 5: 対数変換
    df_log = df.copy()
    for col in [Y_COL, X_MAIN]:
        df_log[f"log_{col}"] = np.log(df_log[col].replace(0, np.nan))
    x_log_adj = [f"log_{X_MAIN}"] + avail_covars
    sens_rows.append(_ols_row("Spec5_Log_Transform", df_log, f"log_{Y_COL}", x_log_adj, cov_type="HC3"))

    # Spec 6: 追加共変量（physicians_per_100k）
    if "physicians_per_100k" in df.columns and df["physicians_per_100k"].notna().any():
        x_extra = x_adj + ["physicians_per_100k"]
        sens_rows.append(_ols_row("Spec6_Extra_Covariate", df, Y_COL, x_extra, cov_type="HC3"))
    else:
        logger.warning("physicians_per_100k が存在しないため Spec6 をスキップ")

    # Spec 7: 追加共変量（dentists_per_100k）← 歯科医師密度仮説の検証
    if "dentists_per_100k" in df.columns and df["dentists_per_100k"].notna().any():
        x_dentist = x_adj + ["dentists_per_100k"]
        sens_rows.append(_ols_row("Spec7_Dentist_Density", df, Y_COL, x_dentist, cov_type="HC3"))
        logger.info("Spec7（dentists_per_100k 追加）を実行")
    else:
        logger.warning("dentists_per_100k が存在しないため Spec7 をスキップ（08_dentist_data.py を実行してください）")

    pd.DataFrame(sens_rows).to_csv(results_dir / "sensitivity_results.csv", index=False, encoding="utf-8-sig")
    sig_count = sum(1 for r in sens_rows if r["p_value"] < 0.05)
    logger.info(f"感度分析: {sig_count}/{len(sens_rows)} 仕様で cancer_surgery_rate が p<0.05")

    # =========================================================================
    # 歯科医師密度との単変量相関（仮説検証）
    # =========================================================================
    if "dentists_per_100k" in df.columns and df["dentists_per_100k"].notna().any():
        from scipy import stats as scipy_stats

        corr_rows = []
        for xvar in [X_MAIN] + avail_covars + ["dentists_per_100k", "physicians_per_100k"]:
            if xvar not in df.columns:
                continue
            sub = df[[Y_COL, xvar]].dropna()
            if len(sub) < 3:
                continue
            r, p = scipy_stats.pearsonr(sub[xvar], sub[Y_COL])
            corr_rows.append({
                "variable": xvar,
                "pearson_r": round(float(r), 4),
                "p_value":   round(float(p), 4),
                "n":         len(sub),
            })
            logger.info(f"相関 {xvar} vs {Y_COL}: r={r:.4f}, p={p:.4f} (n={len(sub)})")

        corr_df = pd.DataFrame(corr_rows)
        corr_path = results_dir / "tables" if (results_dir / "tables").exists() else results_dir
        corr_df.to_csv(corr_path / "correlation_matrix.csv", index=False, encoding="utf-8-sig")
        logger.info(f"単変量相関保存: {corr_path / 'correlation_matrix.csv'}")

    # =========================================================================
    # Moran's I 空間自己相関 → LM検定 → SLM（dtype 修正済み）
    # =========================================================================
    moran_path = results_dir / "morans_i_results.txt"
    try:
        import geopandas as gpd
        from esda.moran import Moran
        from libpysal.weights import Queen

        geojson_path = DATA_ROOT / cfg["input_paths"]["spatial_geojson"]
        geo = gpd.read_file(str(geojson_path))
        # pref_code の型を str に統一（dtype 不一致バグの修正）
        geo["pref_code"] = geo["id"].astype(str).str.zfill(2)
        # SLM のために x_adj の共変量もマージ
        cols_to_merge = ["pref_code", Y_COL] + [c for c in x_adj if c != Y_COL]
        df_merge = df[cols_to_merge].copy()
        df_merge["pref_code"] = df_merge["pref_code"].astype(str).str.zfill(2)
        gdf = geo.merge(df_merge, on="pref_code", how="inner")
        if gdf[Y_COL].isna().any():
            logger.warning(f"Moran's I: {gdf[Y_COL].isna().sum()} 都道府県でアウトカム欠損")
        w = Queen.from_dataframe(gdf, use_index=False)
        w.transform = "r"
        moran = Moran(gdf[Y_COL].fillna(gdf[Y_COL].median()).values, w, permutations=999)
        result_text = (
            f"Moran's I for {Y_COL}:\n"
            f"I = {moran.I:.4f}\n"
            f"p-value (permutation) = {moran.p_sim:.4f}\n"
            f"z-score = {moran.z_sim:.4f}\n"
            f"n_permutations = 999\n"
        )
        moran_path.write_text(result_text, encoding="utf-8")
        logger.info(f"Moran's I = {moran.I:.4f}, p = {moran.p_sim:.4f}")

        # =====================================================================
        # LM検定 + Spatial Lag Model（Moran's I が有意な場合に実行）
        # =====================================================================
        _run_lm_and_slm(df, gdf, w, x_adj, avail_covars, results_dir, logger)

    except Exception as e:
        moran_path.write_text(f"Moran's I skipped: {e}\n", encoding="utf-8")
        logger.warning(f"Moran's I 実行エラー: {e}")

    logger.info(f"回帰・空間統計出力完了: {results_dir}")


if __name__ == "__main__":
    main()
