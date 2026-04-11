"""
「入院」シートの主要がん手術データを確認

外来ではなく、入院シートにがん手術のデータがある可能性を調査。
"""
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parents[3]
medical_file = project_root / "02_Data/raw/NDB_OpenData/No.10/01_医科診療行為（算定回数）/01_公費レセプトを含まないデータ/K_手術/款別都道府県別算定回数.xlsx"

print(f"ファイル: {medical_file.name}\n")
print("=" * 80)
print("「入院」シートの確認")
print("=" * 80)

# 入院シートを読み込み
df = pd.read_excel(medical_file, sheet_name='入院', header=[2, 3])
print(f"\nデータ形状: {df.shape} (行数, 列数)\n")

# カラム構造の確認
code_col = [col for col in df.columns if '分類' in str(col) and 'コード' in str(col)][0]
name_col = [col for col in df.columns if '名称' in str(col)][0]
tokyo_col = ('13', '東京都')

# 主要がん手術コードの確認
print("=" * 80)
print("主要がん手術コードのデータ確認")
print("=" * 80)

target_codes = [
    ('K511', '肺切除術'),
    ('K529-2', '胸腔鏡下食道悪性腫瘍手術'),
    ('K655', '胃切除術'),
    ('K655-2', '腹腔鏡下胃切除術'),
    ('K719', '結腸切除術'),
    ('K719-2', '腹腔鏡下結腸切除術'),
    ('K719-3', '腹腔鏡下結腸悪性腫瘍切除術'),
    ('K740', '直腸切除・切断術'),
    ('K740-2', '腹腔鏡下直腸切除・切断術')
]

available_surgery_codes = []

for target_code, expected_name in target_codes:
    mask = df[code_col].astype(str) == target_code
    matched_rows = df[mask]

    if len(matched_rows) > 0:
        idx = matched_rows.index[0]
        name = df.loc[idx, name_col]
        tokyo_value = df.loc[idx, tokyo_col]

        # マスキングされていないかチェック
        is_masked = tokyo_value == '-' or pd.isna(tokyo_value)

        print(f"\n{target_code}: {name}")
        print(f"  東京都: {tokyo_value}")

        if not is_masked:
            try:
                val = float(str(tokyo_value).replace(',', ''))
                available_surgery_codes.append((target_code, name, val))
                print(f"  ✓ 利用可能（{val:,.0f}件）")
            except:
                print(f"  ✗ マスキング")
        else:
            print(f"  ✗ マスキング")
    else:
        print(f"\n{target_code}: 見つかりませんでした")

# K4-K7系統の全コードで利用可能なものを探索
print("\n\n" + "=" * 80)
print("K4-K7系統の利用可能な手術コード探索")
print("=" * 80)

cancer_keywords = ['悪性', '癌', '切除', '摘出', '根治', '肺', '食道', '胃', '肝', '膵', '結腸', '直腸']

k4_k7_codes = df[df[code_col].astype(str).str.match(r'^K[4-7]')]

available_all = []
for idx in k4_k7_codes.index:
    code = str(k4_k7_codes.loc[idx, code_col])
    name = str(k4_k7_codes.loc[idx, name_col])
    tokyo_value = k4_k7_codes.loc[idx, tokyo_col]

    # がん関連キーワードのチェック
    is_cancer_related = any(keyword in name for keyword in cancer_keywords)

    if is_cancer_related:
        # マスキングされていないかチェック
        if tokyo_value != '-' and not pd.isna(tokyo_value):
            try:
                val = float(str(tokyo_value).replace(',', ''))
                if val > 0:
                    available_all.append((code, name, val))
            except:
                pass

print(f"\n利用可能ながん関連手術コード数: {len(available_all)}")

if len(available_all) > 0:
    # 件数順にソート
    available_all.sort(key=lambda x: x[2], reverse=True)

    print("\n=== 利用可能な手術コード（件数順、上位30件） ===\n")
    for i, (code, name, value) in enumerate(available_all[:30], 1):
        print(f'{i:2d}. {code:8s}: {name[:60]:60s} | 東京都={value:>8,.0f}')

    # 統計サマリー
    total_count = sum(val for _, _, val in available_all)
    avg_count = total_count / len(available_all)
    print(f'\n\n=== 統計サマリー ===')
    print(f'利用可能なコード数: {len(available_all)}')
    print(f'東京都での総手術数: {total_count:,.0f}')
    print(f'平均: {avg_count:,.1f}')
    print(f'最大: {max(val for _, _, val in available_all):,.0f}')
    print(f'最小: {min(val for _, _, val in available_all):,.0f}')
