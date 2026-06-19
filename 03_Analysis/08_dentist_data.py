"""
Script 08: Download and process dentist density by prefecture

Data source: e-Stat Survey of Physicians, Dentists and Pharmacists,
Reiwa 4 (2022) — dentists per 100,000 population in medical facilities.

Direct download (no API key required). Parses Shift-JIS CSV and exports
prefecture-level dentist density for integration in script 03.

Output:
  02_Data/master/dentist_statistics_2022.csv

---

スクリプト 08: 歯科医師密度データの取得・処理

e-Stat 医師・歯科医師・薬剤師統計（令和 4 年）から都道府県別
歯科医師密度を取得し、マスター CSV として保存する。
"""
from __future__ import annotations

import pandas as pd
import requests

from _project_setup import PROJECT_DIR, setup_project_logger

logger = setup_project_logger(
    "perioperative_dentist_data",
    PROJECT_DIR / "03_Analysis" / "logs" / "08_dentist_data.log",
)

# e-Stat 直接ダウンロード URL（API キー不要）
DIRECT_DOWNLOAD_URL = (
    "https://www.e-stat.go.jp/stat-search/file-download"
    "?statInfId=000040155767&fileKind=1"
)
# 出典元ページ
SOURCE_PAGE_URL = (
    "https://www.e-stat.go.jp/stat-search/files"
    "?page=1&layout=datalist&toukei=00450026&tstat=000001135683"
    "&cycle=7&tclass1=000001215100&stat_infid=000040155767"
)

PREF_NAMES = {
    "01": "北海道", "02": "青森県", "03": "岩手県", "04": "宮城県", "05": "秋田県",
    "06": "山形県", "07": "福島県", "08": "茨城県", "09": "栃木県", "10": "群馬県",
    "11": "埼玉県", "12": "千葉県", "13": "東京都", "14": "神奈川県", "15": "新潟県",
    "16": "富山県", "17": "石川県", "18": "福井県", "19": "山梨県", "20": "長野県",
    "21": "岐阜県", "22": "静岡県", "23": "愛知県", "24": "三重県", "25": "滋賀県",
    "26": "京都府", "27": "大阪府", "28": "兵庫県", "29": "奈良県", "30": "和歌山県",
    "31": "鳥取県", "32": "島根県", "33": "岡山県", "34": "広島県", "35": "山口県",
    "36": "徳島県", "37": "香川県", "38": "愛媛県", "39": "高知県", "40": "福岡県",
    "41": "佐賀県", "42": "長崎県", "43": "熊本県", "44": "大分県", "45": "宮崎県",
    "46": "鹿児島県", "47": "沖縄県",
}


def fetch_and_parse_estat_csv() -> pd.DataFrame:
    """
    e-Stat から表3 CSV を直接ダウンロードし、47都道府県の歯科医師密度を返す。

    CSV構造（確認済み）:
      - エンコーディング: cp932
      - 都道府県行: col[0] が "01北海道" のように2桁数字+県名
      - 対象列: col[4] = 医療施設従事者の人口10万対歯科医師数

    Returns:
        pref_code, dentists_per_100k を含む DataFrame（47行）
    """
    logger.info(f"e-Stat CSV ダウンロード中: {DIRECT_DOWNLOAD_URL}")
    resp = requests.get(DIRECT_DOWNLOAD_URL, timeout=30)
    resp.raise_for_status()

    raw_bytes = resp.content
    logger.info(f"ダウンロード完了: {len(raw_bytes):,} bytes")

    # cp932（Shift-JIS）でデコード
    lines = raw_bytes.decode("cp932", errors="replace").splitlines()
    logger.info(f"総行数: {len(lines)}")

    def extract_pref_code(first_field: str) -> str | None:
        """col[0] が "01北海道" 形式なら 2桁コードを返す。"""
        s = first_field.strip()
        if len(s) >= 2 and s[:2].isdigit():
            code = int(s[:2])
            if 1 <= code <= 47:
                return f"{code:02d}"
        return None

    result_rows = []
    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        if len(parts) < 5:
            continue
        pref_code = extract_pref_code(parts[0])
        if pref_code is None:
            continue
        # col[4] = 医療施設従事者（全体）の人口10万対歯科医師数
        raw_val = parts[4].replace("－", "").replace("-", "").strip()
        if not raw_val:
            logger.warning(f"  {pref_code}: col[4] が空 → スキップ")
            continue
        try:
            dentists_val = float(raw_val)
            result_rows.append({"pref_code": pref_code, "dentists_per_100k": dentists_val})
        except ValueError:
            logger.warning(f"  {pref_code}: 値変換失敗 '{raw_val}'")

    result = pd.DataFrame(result_rows)
    logger.info(f"解析完了: {len(result)} 都道府県")
    return result


def main() -> None:
    out_path = PROJECT_DIR / "02_Data" / "master" / "dentist_statistics_2022.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------------------------------------------------------
    # 手動入力済みチェック（dentists_per_100k 列あり）
    # -------------------------------------------------------------------------
    if out_path.exists():
        existing = pd.read_csv(out_path, encoding="utf-8-sig")
        if (
            "dentists_per_100k" in existing.columns
            and existing["dentists_per_100k"].notna().any()
        ):
            logger.info(
                f"既存の dentist_statistics_2022.csv に dentists_per_100k あり "
                f"({existing['dentists_per_100k'].notna().sum()} 都道府県) → スキップ"
            )
            result = existing[["pref_code", "dentists_per_100k"]].copy()
            result["pref_code"] = result["pref_code"].astype(str).str.zfill(2)
            _show_ranking_and_cluster(result)
            return

    # -------------------------------------------------------------------------
    # e-Stat CSV 直接ダウンロード・解析
    # -------------------------------------------------------------------------
    try:
        result = fetch_and_parse_estat_csv()
    except Exception as e:
        logger.error(f"e-Stat CSV 取得・解析エラー: {e}")
        logger.error(
            "\n==============================\n"
            "【手動ダウンロード手順】\n"
            "==============================\n"
            "以下の URL から CSV をダウンロードしてください:\n"
            f"  {SOURCE_PAGE_URL}\n"
            "→「表3 人口10万対歯科医師数・都道府県別」の CSV\n\n"
            "ダウンロード後、都道府県ごとの「医療施設従事者」の\n"
            "人口10万対歯科医師数を以下のファイルに手動入力してください:\n"
            f"  {out_path}\n\n"
            "ファイル形式:\n"
            "  pref_code,dentists_per_100k\n"
            "  01,84.2\n"
            "  ...\n"
            "  47,xx.x\n"
            "=============================="
        )
        return

    if result.empty:
        logger.error("都道府県データを抽出できませんでした。手動でデータを確認してください。")
        return

    if len(result) != 47:
        logger.warning(f"都道府県数が 47 ではありません: {len(result)} 行（確認推奨）")

    # -------------------------------------------------------------------------
    # 保存
    # -------------------------------------------------------------------------
    result.to_csv(out_path, index=False, encoding="utf-8-sig")
    logger.info(f"歯科医師密度保存: {out_path} ({len(result)} 行 × {len(result.columns)} 列)")

    _show_ranking_and_cluster(result)


def _show_ranking_and_cluster(result: pd.DataFrame) -> None:
    """ランキングと HH/LL クラスター検証ログを出力する。"""
    result = result.copy()
    result["pref_code"] = result["pref_code"].astype(str).str.zfill(2)
    result_sorted = result.sort_values("dentists_per_100k", ascending=False).reset_index(drop=True)
    result_sorted["prefecture"] = result_sorted["pref_code"].map(PREF_NAMES)
    result_sorted["rank"] = result_sorted.index + 1

    logger.info("歯科医師密度 上位5:")
    for _, row in result_sorted.head(5).iterrows():
        logger.info(f"  {int(row['rank'])}位 {row['prefecture']}: {row['dentists_per_100k']:.1f} /10万人")
    logger.info("歯科医師密度 下位5:")
    for _, row in result_sorted.tail(5).iterrows():
        logger.info(f"  {int(row['rank'])}位 {row['prefecture']}: {row['dentists_per_100k']:.1f} /10万人")

    # HH/LL クラスターの検証
    hh = {"28": "兵庫県", "33": "岡山県", "41": "佐賀県"}
    ll = {"01": "北海道", "03": "岩手県", "47": "沖縄県"}
    result_idx = result.set_index("pref_code")

    logger.info("【仮説検証】HH クラスター vs LL クラスターの歯科医師密度:")
    for code, name in hh.items():
        if code in result_idx.index:
            val = result_idx.loc[code, "dentists_per_100k"]
            rank = int(result_sorted[result_sorted["pref_code"] == code]["rank"].values[0])
            logger.info(f"  HH {name} ({code}): {val:.1f} /10万人 → 全国 {rank}位")
    for code, name in ll.items():
        if code in result_idx.index:
            val = result_idx.loc[code, "dentists_per_100k"]
            rank = int(result_sorted[result_sorted["pref_code"] == code]["rank"].values[0])
            logger.info(f"  LL {name} ({code}): {val:.1f} /10万人 → 全国 {rank}位")


if __name__ == "__main__":
    main()
