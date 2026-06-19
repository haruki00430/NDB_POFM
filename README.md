# When Universal Coverage Meets Local Capacity
**A Prefectural Ecological Analysis of Perioperative Oral Care in Japan**

**皆保険と地域能力の交差点：日本における周術期口腔ケアの都道府県生態学研究**

---

## Overview / 概要

### English

This repository contains analysis code for a nationwide prefectural ecological study examining regional variation in **perioperative oral functional management (POFM)** across Japan's 47 prefectures using NDB Open Data (fiscal year 2023).

**Key findings**:

- POFM delivery varied **2.25-fold** across prefectures (68,804–154,850 claims per 100,000 population).
- Cancer surgical demand was **not** associated with POFM provision (**0/7** sensitivity specifications).
- **Dentist density** was the strongest predictor (Pearson *r* = 0.617, *p* < 0.0001).
- Significant positive spatial autocorrelation (Moran's *I* = 0.210, *p* = 0.024) and LISA clusters were identified.

**Study design**: Cross-sectional ecological study | N = 47 prefectures | Fiscal Year 2023

**Manuscript**: Saito H, Ohira T. When Universal Coverage Meets Local Capacity: A Prefectural Ecological Analysis of Perioperative Oral Care in Japan. *(In submission, Health Policy, 2026)*

### 日本語

本リポジトリは、NDB オープンデータ（2023 年度）を用い、日本 47 都道府県における**周術期口腔機能管理（POFM）**の地域格差を定量化した全国生態学研究の解析コードを公開するものです。

**主要結果**:

- POFM 算定密度は都道府県間で **2.25 倍**の格差（68,804–154,850 /10 万人）。
- がん手術需要は POFM 提供と**関連なし**（感度分析 **0/7** 仕様）。
- **歯科医師密度**が最強の規定因子（Pearson *r* = 0.617、*p* < 0.0001）。
- 有意な空間的自己相関（Moran's *I* = 0.210、*p* = 0.024）および LISA クラスタを同定。

**研究デザイン**: 横断的生態学的研究 | N = 47 都道府県 | 2023 年度（令和 5 年度）

---

## Data Sources / データソース

| Source | Variables | 説明 |
|--------|-----------|------|
| NDB Open Data No.10 (MHLW, FY2023) | POFM fees (B001-2, B001-3); 16 major cancer surgery K-codes | 周術期口腔管理料・がん手術算定回数 |
| Survey of Physicians, Dentists and Pharmacists 2022 (MHLW / e-Stat) | Dentists per 100,000 population | 歯科医師密度（令和 4 年） |
| Prefecture demographics master (bundled in repo) | Population, aging rate, income, density, physicians/100k | `02_Data/master/prefecture_demographics_covariates.csv` |
| Japan prefecture boundaries (GeoJSON) | Spatial weights for Moran's I / SLM / LISA | 都道府県境界（Queen 隣接） |

> **Note / 注意**: NDB raw data are not included in this repository and are not redistributable. Aggregate open data are available from the Ministry of Health, Labour and Welfare: https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000177182.html
>
> NDB 生データは本リポジトリに含まれておらず、再配布できません。集計オープンデータは厚生労働省ウェブサイトから入手可能です。

---

## Repository Structure / リポジトリ構造

```
NDB_POFM/
├── README.md
├── LICENSE
├── requirements.txt
├── config/
│   └── config.yaml                         # Surgery / POFM codes, paths / 手術・POFMコード・パス設定
├── 02_Data/
│   ├── raw/                                # NDB Excel + GeoJSON (not in repo) / 生データ（リポジトリ外）
│   ├── interim/                            # Intermediate CSV (excluded) / 中間 CSV（除外）
│   └── master/                             # Bundled prefecture masters / 都道府県マスター（同梱）
│       ├── prefecture_demographics_covariates.csv
│       └── dentist_statistics_2022.csv
├── 03_Analysis/
│   ├── 01_data_extraction.py               # NDB extraction / NDB データ抽出
│   ├── 02_calculate_implementation_rate.py # Claim counts merge / 算定回数統合
│   ├── 03_integrate_covariates.py          # Covariates + per-100k rates / 共変量統合・人口補正
│   ├── 04_descriptive_stats.py             # Descriptive statistics / 記述統計
│   ├── 05_regression_spatial.py            # OLS, sensitivity, Moran's I, SLM / 回帰・空間統計
│   ├── 06_visualization.py                 # Choropleth, scatter, forest, LISA / 図表作成
│   ├── 07_power_analysis.py                # Post-hoc power / 事後検定力
│   ├── 08_dentist_data.py                  # e-Stat dentist density download / 歯科医師密度取得
│   ├── prefecture_labels_en.py             # English prefecture labels / 都道府県英語ラベル
│   └── results/                            # Tables and figures / 出力表・図
├── results/
│   └── figures/                            # Manuscript-linked figures / 原稿用図
└── 04_Manuscripts/
    ├── Manuscript_perioperative_oral_care.qmd
    ├── references.bib
    └── vancouver.csl
```

---

## Reproduction / 再現手順

### Prerequisites / 必要環境

- Python ≥ 3.10
- [Quarto](https://quarto.org/) (for manuscript rendering / 論文レンダリング用)

### Repository layout / リポジトリ配置

This repository is **self-contained for prefecture-level covariates** (`02_Data/master/`).  
NDB Open Data Excel files and prefecture GeoJSON must be obtained separately (see Data Preparation).

都道府県マスター共変量はリポジトリに同梱済みです。NDB 生データと GeoJSON のみ別途入手が必要です。

Optional: clone inside `NDB_Research_Hub/projects/` if you already use the shared `02_Data/raw/` tree at the Hub root.

Hub 直下の共有 `02_Data/raw/` を使う場合は、モノレポ内配置でも構いません。

### Installation / インストール

```bash
git clone https://github.com/haruki00430/NDB_POFM.git
cd NDB_POFM
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Data Preparation / データ準備

1. Download NDB Open Data No.10 from MHLW and place Excel files under `02_Data/raw/` as specified in `config/config.yaml`.  
   NDB オープンデータ第 10 回を `config/config.yaml` のパスに従い `02_Data/raw/` に配置してください。

2. Place Japan prefecture GeoJSON at `02_Data/raw/GIS/japan.geojson` (or update `config.yaml`).  
   都道府県境界 GeoJSON を配置してください。

3. (Recommended) Run `08_dentist_data.py` before script 03 to populate dentist density.  
   歯科医師密度を使う解析の前に `08_dentist_data.py` の実行を推奨します。

### Analysis / 解析実行

Run scripts 01 through 07 in order (run 08 before 03 when dentist density is needed):  
スクリプトを以下の順に実行してください（歯科医師密度が必要な場合は 03 の前に 08 を実行）：

```bash
python 03_Analysis/01_data_extraction.py
python 03_Analysis/02_calculate_implementation_rate.py
python 03_Analysis/08_dentist_data.py
python 03_Analysis/03_integrate_covariates.py
python 03_Analysis/04_descriptive_stats.py
python 03_Analysis/05_regression_spatial.py
python 03_Analysis/06_visualization.py
python 03_Analysis/07_power_analysis.py
```

---

## Citation / 引用

If you use this code, please cite the associated manuscript and code repository:  
本コードを使用する場合は、論文とコードリポジトリの両方を引用してください：

**Manuscript**:
> Saito H, Ohira T. When Universal Coverage Meets Local Capacity: A Prefectural Ecological Analysis of Perioperative Oral Care in Japan. *(In submission, Health Policy, 2026)*

**Code repository**:
> Saito H. Analysis code for "When Universal Coverage Meets Local Capacity" [Software]. Zenodo. 2026. https://doi.org/10.5281/zenodo.20756030

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20756030.svg)](https://doi.org/10.5281/zenodo.20756030)

---

## Ethics / 倫理事項

This study used publicly available aggregate data. Individual informed consent was not required, and institutional ethics review was not applicable in accordance with Japanese ethical guidelines for epidemiological research.

本研究は公表集計データを使用しており、個人の同意取得および倫理審査委員会の審査は不要です（「疫学研究に関する倫理指針」に準拠）。

---

## License / ライセンス

Analysis code is released under the [MIT License](LICENSE).  
NDB Open Data is provided by the Ministry of Health, Labour and Welfare of Japan and is not redistributable as part of this repository.

解析コードは MIT ライセンスで公開しています。NDB オープンデータは厚生労働省が提供するものであり、本リポジトリから再配布することはできません。
