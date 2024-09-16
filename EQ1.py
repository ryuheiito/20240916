import os
import pandas as pd
import requests

# Excelファイルから緯度・経度、建物名のデータを読み込む
def read_latlon_excel(file_path):
    df = pd.read_excel(file_path)
    return df

# 緯度・経度からURLを生成する（経度, 緯度の順に修正）
def generate_url(lat,lon):
    url = f"https://www.j-shis.bosai.go.jp/labs/karte/pdf?epoch=Y2024&lon={lon}&lat={lat}"
   
    return url

# PDFをダウンロードして保存する
def download_pdf(url, building_name, output_folder):
    response = requests.get(url)
    if response.status_code == 200:
        # PDFを保存するファイルパス
        output_path = os.path.join(output_folder, f"{building_name}.pdf")
        with open(output_path, 'wb') as file:
            file.write(response.content)
        print(f"{building_name}のPDFをダウンロードしました。")
    else:
        print(f"{building_name}のPDFをダウンロードできませんでした。ステータスコード: {response.status_code}")

# メイン処理
def main():
    # 入力Excelファイルと出力フォルダの指定
    input_file = 'input/latlon.xlsx'
    output_folder = 'output'
    
    # 出力フォルダが存在しない場合は作成
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Excelからデータを読み込み
    df = read_latlon_excel(input_file)
    
    # 緯度・経度からURLを生成してPDFをダウンロード
    for index, row in df.iterrows():
        lat = row['緯度']
        lon = row['経度']
        building_name = row['建物名']
        
        # URLを生成
        url = generate_url(lat, lon)
        
        # PDFをダウンロードして保存
        download_pdf(url, building_name, output_folder)
        print (url)
if __name__ == "__main__":
    main()
