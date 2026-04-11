import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parents[3]
medical_file = project_root / "02_Data/raw/NDB_OpenData/No.10/01_医科診療行為（算定回数）/01_公費レセプトを含まないデータ/K_手術/款別都道府県別算定回数.xlsx"

df = pd.read_excel(medical_file, sheet_name=0, header=[2,3])

code_col = [col for col in df.columns if '分類' in str(col) and 'コード' in str(col)][0]
name_col = [col for col in df.columns if '名称' in str(col)][0]
tokyo_col = ('13', '東京都')

# K4-K7で始まる手術コードを抽出
k4_k7_codes = df[df[code_col].astype(str).str.match(r'^K[4-7]')]

print(f'=== K4-K7系統の手術コード総数: {len(k4_k7_codes)} ===\n')

# マスキングされていない（数値データがある）コードを探す
available_codes = []

for idx in k4_k7_codes.index:
    code = str(k4_k7_codes.loc[idx, code_col])
    name = str(k4_k7_codes.loc[idx, name_col])

    # 東京都のデータをチェック
    tokyo_value = str(k4_k7_codes.loc[idx, tokyo_col])

    # マスキング値でない場合
    if tokyo_value != '-' and tokyo_value != 'nan':
        try:
            val = float(tokyo_value.replace(',', ''))
            if val > 100:  # 東京都で100件以上
                available_codes.append((code, name, val))
        except:
            pass

print(f'利用可能なコード数（東京都で100件以上）: {len(available_codes)}\n')
print('サンプル（最初の30件）:')
for code, name, value in available_codes[:30]:
    print(f'{code}: {name[:45]} | 東京都={value:,.0f}')
