import pandas as pd
import os

"""
NDB_XXX_perioperative_oral_care: データ抽出プロトタイプ
第10回NDBオープンデータのExcelファイルから対象の診療行為コードを抽出し、
都道府県別の集計テーブルを作成する。
"""

def extract_ndb_data(file_path, target_codes):
    """
    NDBオープンデータの都道府県別Excelから指定したコードのデータを抽出する。
    (注: 実際のNDB Excelのシート構造に合わせる必要がある)
    """
    print(f"Loading {file_path}...")
    # TODO: NDBのExcelはヘッダーが複雑なため、skiprows等の調整が必要
    try:
        df = pd.read_excel(file_path, skiprows=1) # 暫定
        # コード列を特定（通常、最初の数列に診療行為コードがある）
        # target_codesに含まれる行のみ抽出
        # 都道府県別の列（47都道府県）を取得し、long formatに変換
        return df
    except Exception as e:
        print(f"Error: {e}")
        return None

# 解析用コードリスト
SURGERY_K_CODES = [
    'K529', 'K655', 'K657', 'K514', 'K719', 'K740' # 主要なものに限定
]
DENTAL_B_CODES = [
    'B001-2'
]

if __name__ == "__main__":
    # プロトタイプ実行用の設定
    print("NDB Data Extraction Prototype Initialized.")
    print(f"Target Surgery Codes: {SURGERY_K_CODES}")
    print(f"Target Dental Codes: {DENTAL_B_CODES}")
    # 今後、02_Data/raw/に配置された実ファイルに対して実行する
