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
| `manuscript_main.docx` | 原稿本体（Main document） | 著者名入り・Single-blind対応済み・Figure 1・2 埋め込み済み |
| `supplementary_material.docx` | 補足資料一括（Supplementary） | AppendixFig A1/A2/A4/A5・Suppl.Fig S1・Suppl.Table S1 全て埋め込み済み |
| `cover_letter_JECP.docx` | カバーレター | pandoc変換済み ✅ |
| `STROBE_checklist.docx` | STROBEチェックリスト | Health Policy版から流用 |
| `Figure1_choropleth_pofm.png` | 本文 Figure 1 POFM Choropleth | 主要図・内容確認済み ✅ |
| `Figure2_lisa_cluster_map.png` | 本文 Figure 2 LISA クラスターマップ | 主要図・内容確認済み ✅ |

> ⚠️ **AppendixFigureA1〜A5 の独立PNG は使用しない**  
> これらはファイル名と内容が一致しないラベル誤りが判明済み。  
> 付録・補足の全図は `supplementary_material.docx` に正しく埋め込まれているため、DOCX 1ファイルで提出する。

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

| 順序 | ファイル | Wiley ファイルタイプ | 備考 |
|------|---------|-------------------|------|
| 1 | `manuscript_main.docx` | Main Document | 本文 + Table 1/2 + Figure 1/2 埋め込み |
| 2 | `supplementary_material.docx` | Supplementary Material for Review | 全付録図・補足表を一括収録 |
| 3 | `cover_letter_JECP.docx` | Cover Letter | |
| 4 | `Figure1_choropleth_pofm.png` | Figure | 本文 Figure 1（POFM choropleth） |
| 5 | `Figure2_lisa_cluster_map.png` | Figure | 本文 Figure 2（LISA cluster map） |
| 6 | `STROBE_checklist.docx` | Additional File for Review but Not for Publication | |

> ❌ **AppendixFigureA1〜A5 の個別PNG はアップロードしない**（ラベル誤り確認済み・DOCX内に正しく埋め込み済み）

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
