# Editorial Manager（Health Policy）投稿手順書

**論文**: When Universal Coverage Meets Local Capacity: A Prefectural Ecological Analysis of Perioperative Oral Care in Japan  
**投稿先**: *Health Policy*（Elsevier）  
**EM URL**: https://www.editorialmanager.com/HEAP/default.aspx  
**作成日**: 2026-06-19

---

## 事前確認

手元に以下を用意してください：

| 必要事項 | 内容 |
|---------|------|
| EM アカウント | `m211039@fmu.ac.jp` で登録済みか確認 |
| 電話番号 | 国際形式（例：`+81-24-547-XXXX`）— 未入力だと Submit 不可のことがある |
| **submission_package/** | 下記ファイル（`python build_submission_package.py` で生成） |
| ORCID × 2名 | HS: `0009-0009-7890-6068` / TO: `0000-0003-4532-7165` |

### submission_package/ ファイル一覧

| ファイル | 内容 |
|---------|------|
| `manuscript_main.docx` | ダブルブラインド原稿（著者名なし・Highlights 冒頭済み） |
| `title_page.docx` | Title page（著者・所属・ORCID・CRediT） |
| `cover_letter.docx` | Cover letter |
| `highlights.docx` | Highlights 5 項目（≤85 文字／行・EM 用） |
| `highlights.txt` | 同上（プレーンテキスト参照用） |
| `STROBE_checklist.docx` | STROBE チェックリスト（Supplementary） |
| `Figure3_choropleth_pofm.png` | 本文 Figure 3（300 dpi） |
| `Figure6_lisa_cluster_map.png` | 本文 Figure 6（300 dpi） |
| `AppendixFigureA1_cancer_surgery.png` | Appendix Figure A1 |
| `AppendixFigureA2_scatter_surgery.png` | Appendix Figure A2 |
| `AppendixFigureA4_forest_sensitivity.png` | Appendix Figure A4 |
| `AppendixFigureA5_scatter_dentist.png` | Appendix Figure A5 |

> Table 1・Table 2・Appendix Table A1・Supplementary Figure S1 は **manuscript_main.docx 内に含まれています**。

### package の再生成

```bash
cd 04_Manuscripts
python build_submission_package.py
```

**原稿の正本**: `submission_package/manuscript_main.docx`（通常ビルドでは上書きしない）。Git 管理コピーは `10Manuscript_health_policy_submission_v1_anonymous.docx`。正本を Git に反映する場合は `--sync-repo`、Git から正本を上書きする場合のみ `--force`。

---

## Step 1 — ログイン・アカウント設定

1. **https://www.editorialmanager.com/HEAP/default.aspx** にアクセス
2. **Login** → `m211039@fmu.ac.jp` + パスワード
   - 初回は **Register** から新規登録
3. **Update My Information** で電話番号・ORCID（HS）を確認

---

## Step 2 — 新規投稿の開始

1. **Submit New Manuscript**
2. **Article Type**: **Original Research**（または Full Length Article）
3. **Peer review**: **Double-anonymized** を確認 → **Proceed**

---

## Step 3 — タイトル・Abstract の入力

**Title**
```
When Universal Coverage Meets Local Capacity: A Prefectural Ecological Analysis of Perioperative Oral Care in Japan
```

**Short title / Running head**
```
Supply-Driven Implementation of Perioperative Oral Care in Japan
```

**Abstract**  
→ `manuscript_main.docx` の Abstract（Background / Objectives / Methods / Results / Conclusions）をコピペ

**Keywords**  
→ メイン原稿末尾の Keywords 行（9 語）を入力

**Highlights**  
→ `highlights.docx` をアップロード（別欄がある場合は 5 行を貼り付けでも可）

---

## Step 4 — 著者情報の入力

**Corresponding author（HS）— 1人目**

| 項目 | 内容 |
|-----|------|
| Name | Haruki Saito |
| Email | m211039@fmu.ac.jp |
| Institution | Fukushima Medical University |
| Department | Department of Epidemiology |
| Country | Japan |
| ORCID | 0009-0009-7890-6068 |
| Corresponding? | **Yes** |

**Co-author（TO）— 2人目**

| 項目 | 内容 |
|-----|------|
| Name | Tetsuya Ohira |
| Institution | Fukushima Medical University |
| ORCID | 0000-0003-4532-7165 |
| Corresponding? | No |

著者順: **Saito → Ohira**

---

## Step 5 — ファイルのアップロード

**Attach Files** で以下をアップロード（Designation は EM 画面の選択肢に合わせて調整）：

| 順番 | ファイル | File Designation（例） |
|:---:|---------|----------------------|
| 1 | `title_page.docx` | **Title Page** |
| 2 | `manuscript_main.docx` | **Manuscript** / **Blinded Manuscript** |
| 3 | `Figure3_choropleth_pofm.png` | **Figure**（Caption: Figure 3） |
| 4 | `Figure6_lisa_cluster_map.png` | **Figure**（Caption: Figure 6） |
| 5 | `cover_letter.docx` | **Cover Letter** |
| 6 | `STROBE_checklist.docx` | **Supplementary Material** / **Checklist** |
| 7 | `AppendixFigureA1_*.png` 〜 `A5_*.png` | **Figure** または **Supplementary Figure** |

> **注意**: Title page を Manuscript に同梱しない（ダブルブラインド）。

各ファイルアップロード後 **Confirm**。

---

## Step 6 — 宣言事項

| 項目 | 内容 |
|-----|------|
| **Conflict of Interest** | The authors declare no conflicts of interest. |
| **Funding** | None declared. |
| **Ethics** | Publicly available aggregate data; ethics review not required. |
| **Data availability** | NDB Open Data (MHLW) + Zenodo `https://doi.org/10.5281/zenodo.20756258` |
| **AI use** | メイン原稿の AI 開示セクションと同内容 |
| **Open Access** | **Subscription route**（非 OA・APC なし）を選択 |

---

## Step 7 — 最終確認と Submit

1. **Build PDF for Approval**（利用可能な場合）でプレビュー
2. 確認項目:
   - [ ] ブラインド原稿に著者名・所属なし
   - [ ] Title page が別ファイルで正しい
   - [ ] 本文図表 4 点（T1, T2, F3, F6）
   - [ ] Research in Context・Highlights あり
   - [ ] Data Availability（Zenodo DOI）
3. **Approve PDF** → **Submit**

送信後、**Manuscript ID**（例：`HEAP-D-26-XXXXX`）をメール・工程表に記録。

---

## よくある問題

| 問題 | 対処 |
|-----|------|
| Submit 不可 | 電話番号・必須項目の未入力を確認 |
| File Designation が見つからない | Supplementary Material / Other を選択 |
| 図が粗い | 300 dpi PNG を再アップロード |

---

## 関連リンク

| 項目 | URL |
|------|-----|
| **Editorial Manager（投稿先）** | https://www.editorialmanager.com/HEAP/default.aspx |
| ジャーナルサイト | https://www.sciencedirect.com/journal/health-policy |
| Zenodo v1.0.3 | https://doi.org/10.5281/zenodo.20756258 |
| GitHub（コード） | https://github.com/haruki00430/NDB_POFM |

---

*正本ワークフロー: `00_Docs/03_Research/perioperative_oral_care_submission_workflow_20260619.md`*
