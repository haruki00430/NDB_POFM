"""
Script 06: Manuscript figures (choropleth, scatter, forest, LISA map)

Generates publication figures at 300 dpi:
  Fig 1: POFM density choropleth
  Fig 2: Cancer surgery density choropleth
  Fig 3: Cancer surgery vs POFM scatter
  Fig 4: Sensitivity analysis forest plot
  Fig 5: LISA cluster map (Local Moran's I)
  Fig 6: Dentist density vs POFM scatter (HH/LL clusters highlighted)

Outputs: results/figures/ and 03_Analysis/results/figures/

---

スクリプト 06: 論文用図表の作成

コロプレス図・散布図・フォレストプロット・LISA クラスタマップを
300 dpi で出力する。
"""
from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from _project_setup import DATA_ROOT, PROJECT_DIR, setup_project_logger

_ANALYSIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_ANALYSIS_DIR))

from prefecture_labels_en import prefecture_label_en

logger = setup_project_logger(
    "perioperative_visualization",
    PROJECT_DIR / "03_Analysis" / "logs" / "06_visualization.log",
)
DPI = 300
CMAP_DENTAL = "OrRd"
CMAP_SURGERY = "Blues"


def _save(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path, dpi=DPI, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"保存: {path.name}")


def choropleth(
    gdf: gpd.GeoDataFrame,
    col: str,
    title: str,
    cmap: str,
    out: Path,
    *,
    legend_label: str | None = None,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 8))
    gdf.plot(
        column=col,
        cmap=cmap,
        linewidth=0.3,
        edgecolor="grey",
        legend=True,
        legend_kwds={"label": legend_label or col},
        missing_kwds={"color": "lightgrey"},
        ax=ax,
    )
    ax.set_title(title, fontsize=13, pad=10)
    ax.axis("off")
    plt.tight_layout()
    _save(fig, out)


def scatter_with_labels(df: pd.DataFrame, x: str, y: str, title: str, xlabel: str, ylabel: str, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(df[x], df[y], alpha=0.7, s=60, color="#2c7bb6", edgecolors="white", linewidth=0.5)
    # 回帰直線
    mask = df[[x, y]].notna().all(axis=1)
    if mask.sum() > 3:
        z = np.polyfit(df.loc[mask, x], df.loc[mask, y], 1)
        p = np.poly1d(z)
        xs = np.linspace(df[x].min(), df[x].max(), 100)
        ax.plot(xs, p(xs), "r--", linewidth=1.2, label="OLS fit")
    # Prefecture labels (top 5 and bottom 5 by outcome)
    top5 = df.nlargest(5, y).index
    bot5 = df.nsmallest(5, y).index
    for i in top5.union(bot5):
        row = df.loc[i]
        ax.annotate(
            prefecture_label_en(str(row["都道府県"])),
            (row[x], row[y]),
            fontsize=7,
            xytext=(3, 3),
            textcoords="offset points",
        )
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.set_title(title, fontsize=12)
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save(fig, out)


def forest_plot(sens_df: pd.DataFrame, out: Path) -> None:
    """感度分析の Forest plot（cancer_surgery_rate の係数）。"""
    fig, ax = plt.subplots(figsize=(9, 6))
    labels = sens_df["model"].tolist()
    coefs = sens_df["coef"].tolist()
    ci_low = sens_df["ci_low"].tolist()
    ci_high = sens_df["ci_high"].tolist()
    pvals = sens_df["p_value"].tolist()

    y_pos = list(range(len(labels)))
    colors = ["#d73027" if p < 0.05 else "#4575b4" for p in pvals]

    ax.axvline(x=0, color="black", linewidth=0.8, linestyle="--", alpha=0.6)
    for i, (y, coef, lo, hi, col) in enumerate(zip(y_pos, coefs, ci_low, ci_high, colors)):
        ax.plot([lo, hi], [y, y], color=col, linewidth=2.0)
        ax.plot(coef, y, "o", color=col, markersize=7, zorder=5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Regression coefficient (cancer surgery density)", fontsize=11)
    ax.set_title(
        "Sensitivity analysis: coefficient for cancer surgery density with 95% CI\n"
        "(red: p<0.05, blue: p≥0.05)",
        fontsize=11,
    )
    sig_patch = mpatches.Patch(color="#d73027", label="p<0.05")
    ns_patch = mpatches.Patch(color="#4575b4", label="p≥0.05")
    ax.legend(handles=[sig_patch, ns_patch], fontsize=9, loc="lower right")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    _save(fig, out)


def lisa_cluster_map(gdf_full: gpd.GeoDataFrame, col: str, out: Path) -> None:
    """
    Local Moran's I によるクラスタ地図 (LISA)。

    クラスタ分類（q 属性）:
      1 = High-High (HH): 高値都道府県が高値隣接に囲まれる → 赤
      2 = Low-High  (LH): 低値都道府県が高値隣接に囲まれる → 水色
      3 = Low-Low   (LL): 低値都道府県が低値隣接に囲まれる → 青
      4 = High-Low  (HL): 高値都道府県が低値隣接に囲まれる → 橙
      NS（p≥0.05）                                          → 薄灰
    """
    try:
        from esda.moran import Moran_Local
        from libpysal.weights import Queen

        # 欠損を除外した GDF で重み行列を構築
        gdf = gdf_full.dropna(subset=[col]).copy().reset_index(drop=True)
        w = Queen.from_dataframe(gdf, use_index=False)
        w.transform = "r"

        moran_loc = Moran_Local(gdf[col].values, w, seed=42, permutations=999)
        gdf["lisa_q"]   = moran_loc.q        # 1=HH, 2=LH, 3=LL, 4=HL
        gdf["lisa_sig"] = moran_loc.p_sim < 0.05

        COLOR_MAP = {1: "#d7191c", 2: "#abd9e9", 3: "#2c7bb6", 4: "#fdae61"}
        NS_COLOR = "#d3d3d3"

        gdf["lisa_color"] = gdf.apply(
            lambda r: COLOR_MAP.get(int(r["lisa_q"]), NS_COLOR) if r["lisa_sig"] else NS_COLOR,
            axis=1,
        )

        # クラスタ件数
        hh = int(((gdf["lisa_q"] == 1) & gdf["lisa_sig"]).sum())
        ll = int(((gdf["lisa_q"] == 3) & gdf["lisa_sig"]).sum())
        lh = int(((gdf["lisa_q"] == 2) & gdf["lisa_sig"]).sum())
        hl = int(((gdf["lisa_q"] == 4) & gdf["lisa_sig"]).sum())
        ns = int(len(gdf) - hh - ll - lh - hl)

        fig, ax = plt.subplots(figsize=(10, 8))

        # 欠損都道府県（孤立ノード等）を薄灰で背景描画
        missing_idx = gdf_full.index.difference(gdf.index)
        if len(missing_idx) > 0:
            gdf_full.loc[missing_idx].plot(ax=ax, color="lightgrey", edgecolor="grey", linewidth=0.3)

        # クラスタ色で各都道府県を描画
        for color in gdf["lisa_color"].unique():
            gdf[gdf["lisa_color"] == color].plot(
                ax=ax, color=color, edgecolor="grey", linewidth=0.3
            )

        # 凡例
        patches = [
            mpatches.Patch(color="#d7191c", label=f"High-High (HH, n={hh})"),
            mpatches.Patch(color="#abd9e9", label=f"Low-High  (LH, n={lh})"),
            mpatches.Patch(color="#2c7bb6", label=f"Low-Low   (LL, n={ll})"),
            mpatches.Patch(color="#fdae61", label=f"High-Low  (HL, n={hl})"),
            mpatches.Patch(color="#d3d3d3", label=f"Not Significant (n={ns})"),
        ]
        ax.legend(handles=patches, loc="lower left", fontsize=9, title="LISA Cluster (p<0.05)")
        ax.set_title(
            "LISA cluster map: perioperative oral management (POFM) density\n"
            "(Global Moran's I = 0.210, p = 0.024; 999 permutations)",
            fontsize=12,
            pad=10,
        )
        ax.axis("off")
        plt.tight_layout()
        _save(fig, out)

    except ImportError:
        logger.warning("esda/libpysal が未インストールのため LISA マップをスキップ")
    except Exception as e:
        logger.warning(f"LISA マップ生成エラー: {e}")
        import traceback
        logger.warning(traceback.format_exc())


def _scatter_dentist_vs_dental(df: pd.DataFrame, out: Path) -> None:
    """
    Figure 6: 歯科医師密度 vs POFM 密度の散布図（仮説検証）。

    HH クラスター（兵庫・岡山・佐賀）を赤、
    LL クラスター（北海道・岩手・沖縄）を青でハイライト。
    """
    HH_CODES = {"28", "33", "41"}  # 兵庫・岡山・佐賀
    LL_CODES  = {"01", "03", "47"}  # 北海道・岩手・沖縄

    x = "dentists_per_100k"
    y = "dental_mgmt_rate"

    mask = df[[x, y]].notna().all(axis=1)
    plot_df = df[mask].copy()

    fig, ax = plt.subplots(figsize=(9, 7))

    # 通常の都道府県（灰色）
    normal_mask = ~plot_df["pref_code"].isin(HH_CODES | LL_CODES)
    ax.scatter(
        plot_df.loc[normal_mask, x], plot_df.loc[normal_mask, y],
        color="#888888", alpha=0.6, s=55, edgecolors="white", linewidth=0.5,
        label="Other prefectures",
    )

    # HH クラスター（赤）
    hh_mask = plot_df["pref_code"].isin(HH_CODES)
    ax.scatter(
        plot_df.loc[hh_mask, x], plot_df.loc[hh_mask, y],
        color="#d7191c", alpha=0.9, s=90, edgecolors="white", linewidth=0.8, zorder=5,
        label="High-High cluster (Hyogo, Okayama, Saga)",
    )

    # LL クラスター（青）
    ll_mask = plot_df["pref_code"].isin(LL_CODES)
    ax.scatter(
        plot_df.loc[ll_mask, x], plot_df.loc[ll_mask, y],
        color="#2c7bb6", alpha=0.9, s=90, edgecolors="white", linewidth=0.8, zorder=5,
        label="Low-Low cluster (Hokkaido, Iwate, Okinawa)",
    )

    # ラベル付け（HH・LL のみ）
    for i, row in plot_df[hh_mask | ll_mask].iterrows():
        ax.annotate(
            prefecture_label_en(str(row["都道府県"])),
            (row[x], row[y]),
            fontsize=8,
            xytext=(4, 4),
            textcoords="offset points",
        )

    # OLS 回帰直線（全都道府県）
    if mask.sum() > 3:
        z = np.polyfit(plot_df[x], plot_df[y], 1)
        p_fit = np.poly1d(z)
        xs = np.linspace(plot_df[x].min(), plot_df[x].max(), 100)
        ax.plot(xs, p_fit(xs), "k--", linewidth=1.2, alpha=0.6, label="OLS fit (all prefectures)")

    ax.set_xlabel("Dentists per 100,000 population (2022)", fontsize=11)
    ax.set_ylabel("POFM claim density per 100,000 population (FY2023)", fontsize=11)
    ax.set_title(
        "Dentist density vs. perioperative oral management (POFM) density\n"
        "(N=47 prefectures; red=High-High LISA cluster, blue=Low-Low LISA cluster)",
        fontsize=11,
    )
    ax.legend(fontsize=9, loc="upper left")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    _save(fig, out)


def main() -> None:
    with open(PROJECT_DIR / "config" / "config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    results_dir = PROJECT_DIR / cfg["output_paths"]["results"]
    figures_dir = PROJECT_DIR / cfg["output_paths"]["figures"]
    figures_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(
        PROJECT_DIR / cfg["output_paths"]["interim"] / cfg["output_paths"]["files"]["analysis_dataset"],
        encoding="utf-8-sig",
    )
    df["pref_code"] = df["pref_code"].astype(str).str.zfill(2)

    # -------------------------------------------------------------------------
    # GeoJSON の読み込み・マージ
    # -------------------------------------------------------------------------
    geo = gpd.read_file(str(DATA_ROOT / cfg["input_paths"]["spatial_geojson"]))
    geo["pref_code"] = geo["id"].astype(str).str.zfill(2)
    merge_cols = ["pref_code", "dental_mgmt_rate", "cancer_surgery_rate"]
    if "dentists_per_100k" in df.columns:
        merge_cols.append("dentists_per_100k")
    gdf = geo.merge(df[merge_cols], on="pref_code", how="left")

    # -------------------------------------------------------------------------
    # Fig 1: dental_mgmt_rate コロプレス
    # -------------------------------------------------------------------------
    choropleth(
        gdf,
        "dental_mgmt_rate",
        "Perioperative oral management (POFM) claim density\n"
        "(B001-2/3 claims per 100,000 population)",
        CMAP_DENTAL,
        figures_dir / "choropleth_dental_mgmt_rate.png",
        legend_label="Claims per 100,000 population",
    )

    # -------------------------------------------------------------------------
    # Fig 2: cancer_surgery_rate コロプレス
    # -------------------------------------------------------------------------
    choropleth(
        gdf,
        "cancer_surgery_rate",
        "Major cancer surgery claim density\n(16 K-codes per 100,000 population)",
        CMAP_SURGERY,
        figures_dir / "choropleth_cancer_surgery_rate.png",
        legend_label="Claims per 100,000 population",
    )

    # -------------------------------------------------------------------------
    # Fig 3: 散布図
    # -------------------------------------------------------------------------
    scatter_with_labels(
        df.reset_index(drop=True),
        x="cancer_surgery_rate",
        y="dental_mgmt_rate",
        title="Cancer surgery density vs. POFM density by prefecture\n(N=47, OLS fit line)",
        xlabel="Cancer surgery claims per 100,000 population",
        ylabel="POFM claims per 100,000 population",
        out=figures_dir / "scatter_surgery_vs_dental.png",
    )

    # -------------------------------------------------------------------------
    # Fig 4: Forest plot（感度分析）
    # -------------------------------------------------------------------------
    sens_path = results_dir / "sensitivity_results.csv"
    if sens_path.exists():
        sens_df = pd.read_csv(sens_path, encoding="utf-8-sig")
        forest_plot(sens_df, figures_dir / "forest_sensitivity.png")
    else:
        logger.warning("sensitivity_results.csv が存在しないため Forest plot をスキップ")

    # -------------------------------------------------------------------------
    # Fig 5: LISA クラスタマップ
    # -------------------------------------------------------------------------
    lisa_cluster_map(
        gdf,
        col="dental_mgmt_rate",
        out=figures_dir / "lisa_cluster_map.png",
    )

    # -------------------------------------------------------------------------
    # Fig 6: 歯科医師密度 vs POFM 密度（仮説検証散布図）
    # -------------------------------------------------------------------------
    if "dentists_per_100k" in df.columns and df["dentists_per_100k"].notna().any():
        _scatter_dentist_vs_dental(
            df.reset_index(drop=True),
            out=figures_dir / "scatter_dentist_vs_dental.png",
        )
    else:
        logger.warning("dentists_per_100k が存在しないため Figure 6 をスキップ（08_dentist_data.py を実行してください）")

    # -------------------------------------------------------------------------
    # 図リスト
    # -------------------------------------------------------------------------
    figure_list = [
        "choropleth_dental_mgmt_rate.png",
        "choropleth_cancer_surgery_rate.png",
        "scatter_surgery_vs_dental.png",
        "forest_sensitivity.png",
        "lisa_cluster_map.png",
        "scatter_dentist_vs_dental.png",
    ]
    pd.DataFrame({"file": figure_list}).to_csv(
        results_dir / "figure_manifest.csv", index=False, encoding="utf-8-sig"
    )
    logger.info(f"全図表出力完了: {figures_dir}")


if __name__ == "__main__":
    main()
