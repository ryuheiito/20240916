import os
import pandas as pd
import requests
import json

# Excelファイルから緯度・経度、建物名のデータを読み込む
def read_latlon_excel(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except FileNotFoundError:
        print(f"Error: ファイル {file_path} が見つかりません。正しいパスを指定してください。")
        return None

# 緯度・経度からURLを生成する
def generate_url(lat, lon):
    return f"https://www.j-shis.bosai.go.jp/map/api/sstrct/V4/meshinfo.geojson?position={lon},{lat}&epsg=4326"

# JSONデータをダウンロード
def fetch_json(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # ステータスコードが200でない場合は例外を発生させる
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: JSONデータの取得に失敗しました。エラー: {e}")
        return None

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
    if df is None:
        return  # ファイルが見つからない場合は終了
    
    # 各緯度・経度からJSONを取得し、JNAMEをcsvに保存
    for index, row in df.iterrows():
        lat = row['緯度']
        lon = row['経度']
        building_name = row['建物名']
        
        # URLを生成
        url = generate_url(lat, lon)
        
        # JSONデータを取得
        json_data = fetch_json(url)
        
        if json_data and "features" in json_data and len(json_data["features"]) > 0:
            jname = json_data["features"][0]["properties"].get("JNAME", "N/A")
            output_data = [{"建物名": building_name, "JNAME": jname}]
            
            # CSVファイル名に「_微地形区分」を追加して出力（utf-8-sigでエンコードして文字化けを防ぐ）
            output_csv = os.path.join(output_folder, f"{building_name}_微地形区分.csv")
            output_df = pd.DataFrame(output_data)
            output_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"{building_name}のデータを{output_csv}に保存しました。")
        else:
            print(f"JNAMEが見つかりませんでした: {building_name}")

if __name__ == "__main__":
    main()
