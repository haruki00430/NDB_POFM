# Journal of Evaluation in Clinical Practice — submission_package_JECP

JECP（Wiley）投稿用ステージングフォルダ。  
**投稿システム**: Wiley Authors portal — https://authors.wiley.com/journal/JEP  
**査読方式**: Single-blind（著者名は査読者に開示される）

---

## Health Policy からの経緯

| 項目 | 内容 |
|------|------|
| 前投稿先 | Health Policy（Elsevier） |
| Manuscript ID | HEAP-D-26-01327 |
| Desk reject 日 | 2026-06-24 |
| Elsevier Transfer 推薦 | 受信済み → **Decline all**（ユーザー操作要） |
| 今回投稿先 | Journal of Evaluation in Clinical Practice（Wiley） |

---

## 原稿ファイルの正本

| 役割 | パス |
|------|------|
| **原稿（著者名入り・投稿版）** | `submission_package_JECP/manuscript_main.docx` |
| 原稿ソース（QMD） | `04_Manuscripts/Manuscript_perioperative_oral_care.qmd` |
| カバーレター（MD） | `04_Manuscripts/cover_letter_JECP.md` |

> **Single-blind 対応済み**: JECP は Single-blind 査読のため著者名を含めて投稿可。  
> `manuscript_main.docx` の Author Contributions には "Haruki Saito" / "Tetsuya Ohira" を明記済み。

---

## ファイル一覧（JECP投稿に必要なもの）

| ファイル | 役割 | 備考 |
|---------|------|------|
| `manuscript_main.docx` | 原稿本体（Main document） | 著者名入り・Single-blind対応済み |
| `cover_letter_JECP.docx` | カバーレター | pandoc変換済み ✅ |
| `STROBE_checklist.docx` | STROBEチェックリスト | Health Policy版から流用 |
| `Figure3_choropleth_pofm.png` | Fig.3 Choropleth地図 | 主要図 |
| `Figure6_lisa_cluster_map.png` | Fig.6 LISA クラスターマップ | 主要図 |
| `AppendixFigureA1_cancer_surgery.png` | 付録図A1 | Supplementary |
| `AppendixFigureA2_scatter_surgery.png` | 付録図A2 | Supplementary |
| `AppendixFigureA4_forest_sensitivity.png` | 付録図A4 | Supplementary |
| `AppendixFigureA5_scatter_dentist.png` | 付録図A5 | Supplementary |

> **Health Policy との差異**: JECP は Highlights 不要。Title Page も不要（Wiley フォームで入力）。

---

## Wiley Authors アップロード手順

### Step 1: ログイン・新規投稿開始
1. https://authors.wiley.com/journal/JEP にアクセス
2. Wiley アカウントでログイン（または新規登録）
3. "Start your submission" をクリック

### Step 2: Article Information
| 項目 | 入力値 |
|------|--------|
| Article type | **Original Paper** |
| Title | When Universal Coverage Meets Local Capacity: A Prefectural Ecological Analysis of Perioperative Oral Care in Japan |
| Running title | Perioperative Oral Care Under Universal Coverage |
| Abstract | 原稿のAbstractをそのまま貼付（構造化済み・約245語） |
| Keywords | perioperative oral care; supply-driven care; universal health coverage; NDB Open Data; ecological study; spatial autocorrelation; Japan |

> **Keywords について**: MeSH推奨。上記7語をそのまま使用可（MeSH確認済みに相当）。

### Step 3: Authors
| 著者 | ORCID | Role |
|------|-------|------|
| Haruki Saito | 0009-0009-7890-6068 | Corresponding author |
| Tetsuya Ohira | 0000-0003-4532-7165 | Co-author |

連絡先メール: m211039@fmu.ac.jp

### Step 4: File Upload（推奨順）

| 順序 | ファイル | Wiley ファイルタイプ |
|------|---------|-------------------|
| 1 | `manuscript_main.docx` | Main Document |
| 2 | `cover_letter_JECP.docx` | Cover Letter |
| 3 | `Figure3_choropleth_pofm.png` | Figure |
| 4 | `Figure6_lisa_cluster_map.png` | Figure |
| 5 | `STROBE_checklist.docx` | Supporting Information |
| 6 | `AppendixFigureA1_cancer_surgery.png` | Supporting Information |
| 7 | `AppendixFigureA2_scatter_surgery.png` | Supporting Information |
| 8 | `AppendixFigureA4_forest_sensitivity.png` | Supporting Information |
| 9 | `AppendixFigureA5_scatter_dentist.png` | Supporting Information |

### Step 5: Ethics & Declarations
| 項目 | 対応 |
|------|------|
| IRB / Ethics statement | 公開集計データ使用・個人情報なし（本文中に記載済み） |
| Data Availability | GitHub + Zenodo DOI を記入 |
| Conflict of Interest | None declared |
| Funding | None declared |
| Previous submission | Health Policy（Elsevier）にて2026-06-24 desk reject（カバーレター記載済み） |

### Step 6: Submit

---

## JECP投稿規定チェックリスト

- [x] Article type: Original Paper（5,000語以内 → 約2,325語 ✓）
- [x] Abstract: 構造化（rationale / aims & objectives / method / results / conclusion）・約245語（300語以内 ✓）
- [x] Running title: "Perioperative Oral Care Under Universal Coverage"（32字 ✓ <50字）
- [x] Keywords: 7語（MeSH準拠）
- [x] ORCID: 両著者分あり
- [x] STROBE checklist 添付
- [x] Data Availability Statement あり
- [x] IRB Statement あり（本文中）
- [x] COI・Funding宣言あり
- [x] 前投稿歴開示（カバーレターに記載）
- [x] Highlights 不要（JECP規定に該当項目なし）
- [x] Title Page 不要（Wileyフォームで入力）
- [x] カバーレター DOCX 変換（pandoc実行 ✅）
- [ ] Wiley Authors portal で投稿完了
