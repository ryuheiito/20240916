import os
import pandas as pd

# フォルダパスとファイルパスの設定
output_folder = './output'
input_file = './input/微地形区分.xlsx'

# 微地形区分.xlsxファイルの読み込み
input_data = pd.read_excel(input_file)

# 微地形区分列のデータを取得
micro_landform_classifications = input_data[['微地形区分', '定義・特徴']]

# outputフォルダ内のCSVファイルを走査
for file_name in os.listdir(output_folder):
    if '微地形区分' in file_name and file_name.endswith('.csv'):
        # CSVファイルの読み込み (エンコーディングの自動切り替え)
        csv_file_path = os.path.join(output_folder, file_name)
        try:
            csv_data = pd.read_csv(csv_file_path, encoding='utf-8')
        except UnicodeDecodeError:
            csv_data = pd.read_csv(csv_file_path, encoding='shift-jis')

        # JNAME列と微地形区分列のデータ型を確認して、一致する項目をマージ
        csv_data['JNAME'] = csv_data['JNAME'].astype(str)
        micro_landform_classifications['微地形区分'] = micro_landform_classifications['微地形区分'].astype(str)

        # JNAME列を基に一致する項目を探し、定義・特徴を追加
        csv_data = pd.merge(csv_data, micro_landform_classifications, left_on='JNAME', right_on='微地形区分', how='left')

        # 上書きでCSVファイルに保存 (UTF-8-sigで保存することでExcelでも正しく開ける)
        csv_data.to_csv(csv_file_path, index=False, encoding='utf-8-sig')

        print(f'処理が完了しました: {csv_file_path}')
