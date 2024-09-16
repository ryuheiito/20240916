import os
import pandas as pd

# フォルダパスとファイルパスの設定
output_folder = './output'
input_file = './input/微地形区分.xlsx'

# 微地形区分.xlsxファイルの読み込み (エンコーディングの考慮は不要)
input_data = pd.read_excel(input_file)

# 微地形区分列のデータを取得
micro_landform_classifications = input_data[['微地形区分', '定義・特徴']]

# outputフォルダ内のCSVファイルを走査
for file_name in os.listdir(output_folder):
    if '微地形区分' in file_name and file_name.endswith('.csv'):
        # CSVファイルの読み込み (Shift-JISエンコーディングを指定)
        csv_file_path = os.path.join(output_folder, file_name)
        try:
            csv_data = pd.read_csv(csv_file_path, encoding='utf-8')
        except UnicodeDecodeError:
            csv_data = pd.read_csv(csv_file_path, encoding='shift-jis')

        # JNAME列を基に一致する項目を探し、定義・特徴を追加
        csv_data = pd.merge(csv_data, micro_landform_classifications, left_on='JNAME', right_on='微地形区分', how='left')

        # 上書きでCSVファイルに保存 (UTF-8で保存、必要ならShift-JISに変更可能)
        csv_data.to_csv(csv_file_path, index=False, encoding='shift-jis')


        print(f'処理が完了しました: {csv_file_path}')
