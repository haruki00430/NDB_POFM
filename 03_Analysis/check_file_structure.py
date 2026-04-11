"""
「款別都道府県別算定回数.xlsx」ファイルの構造を詳細に確認

このファイルが「款」レベル（K4, K5, K6, K7などの大分類）の
集約データを含むかどうかを確認する。
"""
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parents[3]
medical_file = project_root / "02_Data/raw/NDB_OpenData/No.10/01_医科診療行為（算定回数）/01_公費レセプトを含まないデータ/K_手術/款別都道府県別算定回数.xlsx"

print(f"ファイル: {medical_file.name}\n")
print("=" * 80)
print("ファイル構造の確認")
print("=" * 80)

# シート一覧の確認
xl_file = pd.ExcelFile(medical_file)
print(f"\nシート数: {len(xl_file.sheet_names)}")
print(f"シート名: {xl_file.sheet_names}\n")

# 最初のシートを読み込み
df = pd.read_excel(medical_file, sheet_name=0, header=[2, 3])
print(f"データ形状: {df.shape} (行数, 列数)\n")

# カラム構造の確認
code_col = [col for col in df.columns if '分類' in str(col) and 'コード' in str(col)][0]
name_col = [col for col in df.columns if '名称' in str(col)][0]

print("=" * 80)
print("コード列の内容確認（最初の100行）")
print("=" * 80)

# コードのパターンを確認
codes = df[code_col].dropna().astype(str).tolist()[:100]

# K4, K5, K6, K7など2桁コードの有無をチェック
section_codes = []
detailed_codes = []

for code in codes:
    if code.startswith('K') and len(code) <= 3:  # K4, K5, K6など
        section_codes.append(code)
    else:
        detailed_codes.append(code)

print(f"\n款レベルコード（K4, K5等）の数: {len(section_codes)}")
if len(section_codes) > 0:
    print(f"サンプル: {section_codes[:10]}")

print(f"\n詳細コード（K374-2, K511等）の数: {len(detailed_codes)}")
if len(detailed_codes) > 0:
    print(f"サンプル: {detailed_codes[:10]}")

# K4, K5, K6, K7レベルのコードがあるか検索
print("\n" + "=" * 80)
print("款レベル集約データの探索")
print("=" * 80)

k_sections = ['K4', 'K5', 'K6', 'K7']
tokyo_col = ('13', '東京都')

for k_section in k_sections:
    # 完全一致で検索
    mask = df[code_col].astype(str) == k_section
    matched_rows = df[mask]

    if len(matched_rows) > 0:
        print(f"\n【{k_section}】が見つかりました:")
        for idx in matched_rows.index:
            code = df.loc[idx, code_col]
            name = df.loc[idx, name_col]
            tokyo_value = df.loc[idx, tokyo_col]
            print(f"  コード: {code}")
            print(f"  名称: {name}")
            print(f"  東京都: {tokyo_value}")
    else:
        print(f"\n【{k_section}】は見つかりませんでした")

# K4*, K5*, K6*, K7*で始まる行の統計
print("\n" + "=" * 80)
print("各款系統のコード数")
print("=" * 80)

for k_section in k_sections:
    mask = df[code_col].astype(str).str.startswith(k_section)
    count = mask.sum()
    print(f"{k_section}系統: {count}件")

# K511, K655, K719などの主要手術コードの確認
print("\n" + "=" * 80)
print("主要がん手術コードの確認")
print("=" * 80)

target_codes = ['K511', 'K655', 'K719', 'K719-2', 'K529-2']
for target_code in target_codes:
    mask = df[code_col].astype(str) == target_code
    matched_rows = df[mask]

    if len(matched_rows) > 0:
        idx = matched_rows.index[0]
        name = df.loc[idx, name_col]
        tokyo_value = df.loc[idx, tokyo_col]
        print(f"\n{target_code}: {name}")
        print(f"  東京都: {tokyo_value} {'（マスキング）' if tokyo_value == '-' else ''}")
    else:
        print(f"\n{target_code}: 見つかりませんでした")
