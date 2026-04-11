> **正本リポジトリ（GitHub Private）：** https://github.com/haruki00430/NDB_XXX_perioperative_oral_care

# NDB_XXX_perioperative_oral_care

## ステータス（2026-04-08 更新）

- 原稿: これから作成（`04_Manuscripts/Manuscript_perioperative_oral_care.qmd`）
- 実装計画の正本: `00_Docs/02_Implementation/implementation_plan_NDB_XXX_perioperative_oral_care.md`
- `projects/NDB_XXX_perioperative_oral_care/00_Docs/implementation_plan.md` は要約メモとして扱う

## テーマ

癌周術期における医科歯科連携（周術期口腔機能管理）の地域格差を都道府県単位で定量化する。

## 指標定義（現行）

- 分母: `medical_surgery.target_surgery_codes` の都道府県別算定回数合計
- 分子: `dental_management.target_codes`（`B001-2`, `B001-3`）の都道府県別算定回数合計
- 主要アウトカム: 周術期口腔ケア実施率（%）

抽出ロジック（`01_data_extraction.py`）: 医科・歯科とも **「分類コード」列**（「診療行為コード」数値列と区別）を用い、Excel 上で分類コードが空の **継続行**は直前行と同一ブロックとして前方埋めし合算する（`aggregate_classification_subrows`）。これにより K463 等の継続行が分母から漏れない。

解釈: 分子・分母はいずれも **レセプト算定回数**であり、対象疾患・術式が一致する患者母集団比ではない。値は \((\text{分子}/\text{分母})\times 100\) なので **100 を大きく超えうる**（生態学的な「口腔ケア算定回数 ÷ 選択術式算定回数」のスケール）。

注: 「計画策定料」を分子に追加する運用は現行版では採用しない。追加時は `config.yaml` と Methods を同時更新する。

## ディレクトリ構成（実体）

```text
NDB_XXX_perioperative_oral_care/
├── README.md
├── config/
│   └── config.yaml
├── 00_Docs/
│   └── implementation_plan.md                  # 要約メモ
├── 02_Data/
│   ├── interim/                                # 中間CSV（本パイプライン出力）
│   └── master/                                 # プロジェクト専用外部統計CSV
├── 03_Analysis/
│   ├── 01_data_extraction.py
│   ├── 02_calculate_implementation_rate.py
│   ├── 03_integrate_covariates.py
│   ├── 04_descriptive_stats.py
│   ├── 05_regression_spatial.py
│   ├── 06_visualization.py
│   ├── check_*.py                              # 調査用（例: check_code_column_mapping.py）
│   ├── scripts/01_extract_data.py              # 旧プロトタイプ（参照用）
│   ├── logs/
│   └── results/
│       ├── tables/
│       └── figures/
└── 04_Manuscripts/
    ├── AI_USE_DISCLOSURE.md
    ├── Manuscript_perioperative_oral_care.qmd
    └── references.bib
```

## 入出力パス方針

- 生データ: `02_Data/raw/`（読取専用）
- 中間: `projects/NDB_XXX_perioperative_oral_care/02_Data/interim/`
- 結果: `projects/NDB_XXX_perioperative_oral_care/03_Analysis/results/`
- 既存の `projects/NDB_XXX_perioperative_oral_care/results/implementation_rate_by_prefecture.csv` は移行前成果として残置

## 実行順序（再現手順）

```bash
python projects/NDB_XXX_perioperative_oral_care/03_Analysis/01_data_extraction.py
python projects/NDB_XXX_perioperative_oral_care/03_Analysis/02_calculate_implementation_rate.py
python projects/NDB_XXX_perioperative_oral_care/03_Analysis/03_integrate_covariates.py
python projects/NDB_XXX_perioperative_oral_care/03_Analysis/04_descriptive_stats.py
python projects/NDB_XXX_perioperative_oral_care/03_Analysis/05_regression_spatial.py
python projects/NDB_XXX_perioperative_oral_care/03_Analysis/06_visualization.py
```

## 論文レンダリング

```bash
quarto render projects/NDB_XXX_perioperative_oral_care/04_Manuscripts/Manuscript_perioperative_oral_care.qmd --to docx
quarto render projects/NDB_XXX_perioperative_oral_care/04_Manuscripts/Manuscript_perioperative_oral_care.qmd --to html
```

## 関連ドキュメント

- `00_Docs/02_Implementation/implementation_plan_NDB_XXX_perioperative_oral_care.md`（正本）
- `projects/NDB_XXX_perioperative_oral_care/04_Manuscripts/AI_USE_DISCLOSURE.md`
- `CLAUDE.md`
