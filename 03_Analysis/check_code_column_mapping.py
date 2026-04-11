"""
NDB 歯科・医科の「都道府県別算定回数」Excelで、分類コード列と継続行の扱いを検証する。

生データは読み取りのみ。コンソールに列名・行数・東京都の手計算用合計を出力する。
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.ndb_library.logger import setup_logger

logger = setup_logger("check_code_mapping", log_file=str(PROJECT_DIR / "03_Analysis" / "logs" / "check_code_column_mapping.log"))


def resolve_classification_code_column(df: pd.DataFrame):
    """分類コード列（MultiIndex）を特定する。"""
    candidates = [c for c in df.columns if "分類" in str(c) and "コード" in str(c)]
    if candidates:
        return candidates[0]
    alt = [c for c in df.columns if "コード" in str(c)]
    if not alt:
        raise ValueError("コード列が見つかりません")
    logger.warning("分類コード列が見つからず、先頭のコード列を使用: %s", alt[0])
    return alt[0]


def effective_codes(series: pd.Series, aggregate_subrows: bool) -> pd.Series:
    """集約後の分類コード（行単位）。aggregate_subrows 時は前方埋め。"""
    if aggregate_subrows:
        filled = series.ffill()
    else:
        filled = series
    out = pd.Series(pd.NA, index=series.index, dtype="string")
    valid = filled.notna()
    out.loc[valid] = filled[valid].astype(str).str.strip()
    return out


def tokyo_col(df: pd.DataFrame):
    """東京都列 (('13','東京都')) を返す。無ければ None。"""
    for c in df.columns:
        if isinstance(c, tuple) and len(c) == 2 and str(c[0]).zfill(2) == "13":
            return c
    return None


def main() -> None:
    cfg_path = PROJECT_DIR / "config" / "config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    med_path = REPO_ROOT / cfg["medical_surgery"]["data_path"]
    den_path = REPO_ROOT / cfg["dental_management"]["data_path"]
    med_df = pd.read_excel(med_path, sheet_name=cfg["medical_surgery"]["sheet_name"], header=[2, 3])
    den_df = pd.read_excel(den_path, sheet_name=0, header=[2, 3])

    med_cc = resolve_classification_code_column(med_df)
    den_cc = resolve_classification_code_column(den_df)
    print("=== 医科 K_手術 / 入院 ===")
    print("分類コード列:", med_cc)
    print("コードを含む列数:", len([c for c in med_df.columns if "コード" in str(c)]))
    tc = tokyo_col(med_df)
    print("東京都列:", tc)
    k_targets = [x["code"] for x in cfg["medical_surgery"]["target_surgery_codes"]]
    for agg in (False, True):
        eff = effective_codes(med_df[med_cc], aggregate_subrows=agg)
        m = eff.isin(k_targets)
        sub = med_df.loc[m]
        tot = pd.to_numeric(sub[tc], errors="coerce").fillna(0).sum() if tc is not None else float("nan")
        print(f"  対象行数 (aggregate_subrows={agg}): {m.sum()}  東京都合計: {tot:,.0f}")

    print("\n=== 歯科 B_医学管理等 ===")
    print("分類コード列:", den_cc)
    tc_d = tokyo_col(den_df)
    print("東京都列:", tc_d)
    b_targets = [x["code"] for x in cfg["dental_management"]["target_codes"]]
    for agg in (False, True):
        eff = effective_codes(den_df[den_cc], aggregate_subrows=agg)
        m = eff.isin(b_targets)
        sub = den_df.loc[m]
        tot = pd.to_numeric(sub[tc_d], errors="coerce").fillna(0).sum() if tc_d is not None else float("nan")
        print(f"  対象行数 (aggregate_subrows={agg}): {m.sum()}  東京都合計: {tot:,.0f}")

    # B001-2 ブロックの先頭数行（確認用）
    eff_d = effective_codes(den_df[den_cc], aggregate_subrows=True)
    idx = eff_d[eff_d == "B001-2"].index[:1]
    if len(idx):
        i0 = den_df.index.get_loc(idx[0])
        sl = range(max(0, i0 - 1), min(len(den_df), i0 + 6))
        print("\n歯科 B001-2 付近（分類コード・診療行為コード・東京都）:")
        den_proc = [c for c in den_df.columns if "診療行為" in str(c) and "コード" in str(c)]
        proc_c = den_proc[0] if den_proc else None
        for j in sl:
            row = den_df.iloc[j]
            v_tokyo = pd.to_numeric(row[tc_d], errors="coerce") if tc_d else None
            print(
                j,
                row[den_cc],
                row[proc_c] if proc_c is not None else "",
                f"tokyo={v_tokyo}",
            )


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
