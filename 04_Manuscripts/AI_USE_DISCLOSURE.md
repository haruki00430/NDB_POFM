# 生成AI・エージェント利用開示（論文別）

> 本ファイルは [00_Docs/templates/AI_USE_DISCLOSURE.template.md](../../../00_Docs/templates/AI_USE_DISCLOSURE.template.md) に基づく。運用は [CIRCS_NDB_MANUSCRIPT_AI_RULEBOOK.md](../../../00_Docs/07_Setup/CIRCS_NDB_MANUSCRIPT_AI_RULEBOOK.md) を参照。

---

## メタデータ

| 項目 | 内容 |
|------|------|
| 論文仮題 | 癌周術期における医科歯科連携（周術期口腔機能管理）の地域格差 |
| 論文仮題（英語） | Regional disparities in perioperative oral care for major cancer surgery |
| プロジェクトパス | `projects/NDB_XXX_perioperative_oral_care/` |
| 対象誌（候補） | Journal of Epidemiology ほか（追記可） |
| 最終更新日 | 2026-04-08 |
| 記録責任者 | 通信著者（Quarto 配置後、YAML `author` と同一人物に更新） |

**原稿の正本**: `04_Manuscripts/Manuscript_perioperative_oral_care.qmd`。実装計画の正本は [`../../../00_Docs/02_Implementation/implementation_plan_NDB_XXX_perioperative_oral_care.md`](../../../00_Docs/02_Implementation/implementation_plan_NDB_XXX_perioperative_oral_care.md)。

---

## 使用ツール一覧

| ツール・サービス | 区分 | モデル・バージョン（分かる範囲） | 主な用途 |
|------------------|------|----------------------------------|----------|
| Cursor | クラウドエージェント（設定依存） | 利用時点のエージェントモデル | `03_Analysis` 抽出・統合・可視化・将来の原稿 |
| LM Studio 等 | ローカル | — | 使用時は追記 |

**注**: AIを著者にしない。

---

## 研究段階別の利用

### 1. データ整備・ETL・スクリプト生成

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-08 | Cursor 等 | `01_data_extraction.py` / `02_calculate_implementation_rate.py` / `03_integrate_covariates.py` の整備 | `03_Analysis/logs/` |

### 2. 探索的スクリーニング／ローカルLLM

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| — | — | **該当なし**（用いた場合は追記） |  |

### 3. 確証的分析・可視化

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-08 | Cursor 等 | `04_descriptive_stats.py` / `05_regression_spatial.py` / `06_visualization.py` を追加 | `03_Analysis/results/` |

### 4. 原稿

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-08 | Cursor 等 | `Manuscript_perioperative_oral_care.qmd` 初版作成 | `04_Manuscripts/` |

### 5. 参考文献

| 日付 | ツール | 実施内容（1行） | 備考 |
|------|--------|-----------------|------|
| 2026-04-08 | Cursor 等 | `references.bib` 初版作成 | `04_Manuscripts/` |

---

## データ境界

### 外部クラウドLLMに**送らなかった**もの

- [x] NDB 生データの実数値・スクリーンショット
- [x] 個票・再識別可能な細集計の丸貼り

### 送ったもの（機微度が低い範囲）

| 種別 | 例 |
|------|-----|
| メタデータ・コード | 列名、スクリプト、パス |

### ローカルLLMに入力したもの

| 種別 | 例 |
|------|-----|
| （追記） |  |

---

## 人間による検証

| 段階 | 確認内容 | 実施者 | 日付 |
|------|----------|--------|------|
| コード・数値・引用・解釈 | 手術・口腔管理コードの定義 | 著者 | （追記） |

---

## 投稿用短文ドラフト

### 日本語（案）

本研究の原稿作成および解析に生成AI支援ツールを用いた場合、その範囲を開示する。手法・解釈は著者が検証した。AIは著者としない。

### English (draft)

If AI-assisted tools were used, the authors disclose their scope and verified outputs. AI was not listed as an author.

---

## 変更履歴

| 日付 | 変更内容 |
|------|----------|
| 2026-04-08 | 初版（`04_Manuscripts` 新設に伴い作成） |
| 2026-04-08 | パイプライン実装（01〜06）と原稿初版に合わせて段階別ログを更新 |
