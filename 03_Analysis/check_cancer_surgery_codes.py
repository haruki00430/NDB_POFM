"""
がん手術コードの探索スクリプト

K4-K7系統の手術で、「悪性腫瘍」「悪性新生物」「癌」「がん」などを含む
手術コードを抽出し、東京都でマスキングされていないものを確認する。
"""
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parents[3]
medical_file = project_root / "02_Data/raw/NDB_OpenData/No.10/01_医科診療行為（算定回数）/01_公費レセプトを含まないデータ/K_手術/款別都道府県別算定回数.xlsx"

print(f"ファイル読み込み中: {medical_file.name}")
df = pd.read_excel(medical_file, sheet_name=0, header=[2,3])

code_col = [col for col in df.columns if '分類' in str(col) and 'コード' in str(col)][0]
name_col = [col for col in df.columns if '名称' in str(col)][0]
tokyo_col = ('13', '東京都')

# K4-K7で始まる手術コードを抽出
k4_k7_codes = df[df[code_col].astype(str).str.match(r'^K[4-7]')]

print(f'\n=== K4-K7系統の手術コード総数: {len(k4_k7_codes)} ===\n')

# がん関連のキーワードでフィルタリング
cancer_keywords = ['悪性腫瘍', '悪性新生物', '癌', 'がん', '根治', '切除術', '摘出術', '食道', '肺', '胃', '結腸', '直腸', '肝', '膵', '乳房']

cancer_codes = []
for idx in k4_k7_codes.index:
    code = str(k4_k7_codes.loc[idx, code_col])
    name = str(k4_k7_codes.loc[idx, name_col])

    # がん関連キーワードのチェック
    is_cancer_related = any(keyword in name for keyword in cancer_keywords)

    if is_cancer_related:
        # 東京都のデータをチェック
        tokyo_value = str(k4_k7_codes.loc[idx, tokyo_col])

        # マスキング値でない場合
        if tokyo_value != '-' and tokyo_value != 'nan':
            try:
                val = float(tokyo_value.replace(',', ''))
                cancer_codes.append((code, name, val, tokyo_value != '-'))
            except:
                # マスキング値として記録
                cancer_codes.append((code, name, 0, False))
        else:
            # マスキング値として記録
            cancer_codes.append((code, name, 0, False))

print(f'がん関連手術コード総数: {len(cancer_codes)}\n')

# マスキングされていないコード
available_codes = [(code, name, val) for code, name, val, available in cancer_codes if available and val > 0]
print(f'利用可能なコード数（東京都でマスキングなし）: {len(available_codes)}\n')

if len(available_codes) > 0:
    print('=== 利用可能ながん手術コード（東京都での件数順） ===\n')
    # 件数順にソート
    available_codes.sort(key=lambda x: x[2], reverse=True)

    for i, (code, name, value) in enumerate(available_codes[:50], 1):
        print(f'{i:2d}. {code:8s}: {name[:60]:60s} | 東京都={value:>8,.0f}')

# マスキングされているコード
masked_codes = [(code, name) for code, name, val, available in cancer_codes if not available or val == 0]
print(f'\n\nマスキングされているコード数: {len(masked_codes)}')
if len(masked_codes) > 0:
    print('\nマスキングされているがん手術コード（サンプル最初の20件）:')
    for i, (code, name) in enumerate(masked_codes[:20], 1):
        print(f'{i:2d}. {code:8s}: {name[:60]}')

# 統計サマリー
if len(available_codes) > 0:
    total_count = sum(val for _, _, val in available_codes)
    avg_count = total_count / len(available_codes)
    print(f'\n\n=== 統計サマリー ===')
    print(f'東京都での総手術数: {total_count:,.0f}')
    print(f'平均: {avg_count:,.1f}')
    print(f'最大: {max(val for _, _, val in available_codes):,.0f}')
    print(f'最小: {min(val for _, _, val in available_codes):,.0f}')
