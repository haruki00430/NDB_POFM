"""
主要手術コードの探索スクリプト（改良版）

周術期口腔ケアが推奨される主要手術を、より包括的に抽出する。
- K5: 胸部（肺、食道等）の切除術・摘出術
- K6: 腹部（胃、肝臓、膵臓等）の切除術・摘出術
- K7: 消化管（大腸、直腸等）の切除術・摘出術

名称に「悪性」が含まれなくても、実質的にがん患者に多く実施される手術を対象とする。
"""
import pandas as pd
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

project_root = Path(__file__).resolve().parents[3]
medical_file = project_root / "02_Data/raw/NDB_OpenData/No.10/01_医科診療行為（算定回数）/01_公費レセプトを含まないデータ/K_手術/款別都道府県別算定回数.xlsx"

print(f"ファイル読み込み中: {medical_file.name}\n")
df = pd.read_excel(medical_file, sheet_name=0, header=[2,3])

code_col = [col for col in df.columns if '分類' in str(col) and 'コード' in str(col)][0]
name_col = [col for col in df.columns if '名称' in str(col)][0]
tokyo_col = ('13', '東京都')

# K5-K7系統の主要手術キーワード
major_surgery_keywords = [
    # K5: 胸部
    '食道切除', '食道悪性', '肺切除', '肺悪性', '肺葉切除', '胸腔鏡',
    # K6: 腹部
    '胃切除', '胃悪性', '胃全摘', '肝切除', '肝悪性', '膵切除', '膵悪性', '膵頭',
    # K7: 消化管
    '結腸切除', '結腸悪性', '直腸切除', '直腸悪性', '腸切除',
    # その他の重要な手術
    '根治', '摘出術', '拡大'
]

# 除外キーワード（良性の処置）
exclude_keywords = ['ポリープ', '異物', '止血', '狭窄拡張', '瘻', '造設', '抜去']

# K5-K7で始まる手術コードを抽出
k5_k7_codes = df[df[code_col].astype(str).str.match(r'^K[5-7]')]

print(f'=== K5-K7系統の手術コード総数: {len(k5_k7_codes)} ===\n')

major_surgery_codes = []
for idx in k5_k7_codes.index:
    code = str(k5_k7_codes.loc[idx, code_col])
    name = str(k5_k7_codes.loc[idx, name_col])

    # 主要手術キーワードのチェック
    is_major_surgery = any(keyword in name for keyword in major_surgery_keywords)

    # 除外キーワードのチェック
    is_excluded = any(keyword in name for keyword in exclude_keywords)

    if is_major_surgery and not is_excluded:
        # 東京都のデータをチェック
        tokyo_value = str(k5_k7_codes.loc[idx, tokyo_col])

        # マスキング値でない場合
        if tokyo_value != '-' and tokyo_value != 'nan':
            try:
                val = float(tokyo_value.replace(',', ''))
                major_surgery_codes.append((code, name, val, True))
            except:
                major_surgery_codes.append((code, name, 0, False))
        else:
            major_surgery_codes.append((code, name, 0, False))

print(f'主要手術コード総数（キーワード該当）: {len(major_surgery_codes)}\n')

# マスキングされていないコード
available_codes = [(code, name, val) for code, name, val, available in major_surgery_codes if available and val > 0]
print(f'利用可能なコード数（東京都でマスキングなし）: {len(available_codes)}\n')

if len(available_codes) > 0:
    print('=== 利用可能な主要手術コード（東京都での件数順） ===\n')
    # 件数順にソート
    available_codes.sort(key=lambda x: x[2], reverse=True)

    # 臓器別にグループ化して表示
    print('【肺・胸部手術】')
    chest_codes = [(c, n, v) for c, n, v in available_codes if any(k in n for k in ['肺', '胸腔', '食道'])]
    for i, (code, name, value) in enumerate(chest_codes, 1):
        print(f'  {code:8s}: {name[:60]:60s} | 東京都={value:>6,.0f}')

    print('\n【胃・腹部手術】')
    stomach_codes = [(c, n, v) for c, n, v in available_codes if any(k in n for k in ['胃', '肝', '膵'])]
    for i, (code, name, value) in enumerate(stomach_codes, 1):
        print(f'  {code:8s}: {name[:60]:60s} | 東京都={value:>6,.0f}')

    print('\n【大腸・直腸手術】')
    colon_codes = [(c, n, v) for c, n, v in available_codes if any(k in n for k in ['結腸', '直腸', '腸'])]
    for i, (code, name, value) in enumerate(colon_codes, 1):
        print(f'  {code:8s}: {name[:60]:60s} | 東京都={value:>6,.0f}')

    print('\n【その他】')
    other_codes = [x for x in available_codes if x not in chest_codes + stomach_codes + colon_codes]
    for i, (code, name, value) in enumerate(other_codes, 1):
        print(f'  {code:8s}: {name[:60]:60s} | 東京都={value:>6,.0f}')

# マスキングされているコード
masked_codes = [(code, name) for code, name, val, available in major_surgery_codes if not available or val == 0]
print(f'\n\nマスキングされているコード数: {len(masked_codes)}')
if len(masked_codes) > 0:
    print('\nマスキングされている主要手術コード（サンプル最初の30件）:')
    for i, (code, name) in enumerate(masked_codes[:30], 1):
        print(f'{i:2d}. {code:8s}: {name[:60]}')

# 統計サマリー
if len(available_codes) > 0:
    total_count = sum(val for _, _, val in available_codes)
    avg_count = total_count / len(available_codes)
    print(f'\n\n=== 統計サマリー ===')
    print(f'利用可能な主要手術コード数: {len(available_codes)}')
    print(f'東京都での総手術数: {total_count:,.0f}')
    print(f'平均: {avg_count:,.1f}')
    print(f'最大: {max(val for _, _, val in available_codes):,.0f}')
    print(f'最小: {min(val for _, _, val in available_codes):,.0f}')

# 推奨コードリストの出力
print(f'\n\n=== 推奨コードリスト（config.yaml用） ===')
print('\ntarget_surgery_codes:')
for code, name, value in available_codes:
    # 臓器分類を判定
    if any(k in name for k in ['肺', '食道', '胸腔']):
        organ = '胸部'
    elif any(k in name for k in ['胃', '肝', '膵']):
        organ = '腹部'
    elif any(k in name for k in ['結腸', '直腸', '腸']):
        organ = '消化管'
    else:
        organ = 'その他'

    print(f'  - code: "{code}"')
    print(f'    name: "{name}"')
    print(f'    organ: "{organ}"')
    print(f'    tokyo_count: {value:.0f}')
