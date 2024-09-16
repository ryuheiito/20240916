import os
import pandas as pd
import requests
import json

# Excelファイルから緯度・経度、建物名のデータを読み込む
def read_latlon_excel(file_path):
    df = pd.read_excel(file_path)
    return df

# 緯度・経度からURLを生成する
def generate_url(lat, lon):
    url = f"https://www.j-shis.bosai.go.jp/map/api/fltsearch?position={lon},{lat}&epsg=4326&mode=C&version=Y2024&case=AVR&period=P_T30&format=json"
    return url

# JSONデータをダウンロード
def fetch_json(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"JSONの取得に失敗しました。ステータスコード: {response.status_code}")
        return None

# ijmaが大きい順にデータを抽出し、ltename, magnitude, ijma, ltecodeをCSVで出力する
def process_json_data(json_data):
    fault_data = []
    
    if json_data and "Fault" in json_data:
        for fault in json_data["Fault"]:
            ltename = fault.get("ltename", "")
            magnitude = fault.get("magnitude", "")
            ijma = fault.get("ijma", "")
            ltecode = fault.get("ltecode", "")
            fault_data.append({
                "ltecode": ltecode,
                "ltename": ltename,
                "magnitude": magnitude,
                "ijma": float(ijma) if ijma else 0  # ijmaが空でない場合のみ数値に変換
            })
            
            # Patternデータが存在する場合、そのデータも追加
            if "Pattern" in fault:
                for pattern in fault["Pattern"]:
                    ltecode = pattern.get("ltecode", "")
                    ltename = pattern.get("ltename", "")
                    magnitude = pattern.get("magnitude", "")
                    ijma = pattern.get("ijma", "")
                    fault_data.append({
                        "ltecode": ltecode,
                        "ltename": ltename,
                        "magnitude": magnitude,
                        "ijma": float(ijma) if ijma else 0
                    })
    
    # ijmaが大きい順にソート
    sorted_data = sorted(fault_data, key=lambda x: x["ijma"], reverse=True)
    
    return pd.DataFrame(sorted_data)

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
    
    # 各緯度・経度からデータを取得し、CSVで出力
    for index, row in df.iterrows():
        lat = row['緯度']
        lon = row['経度']
        building_name = row['建物名']
        
        # URLを生成
        url = generate_url(lat, lon)
        
        # JSONデータを取得
        json_data = fetch_json(url)
        
        if json_data:
            # ijmaが大きい順にデータを処理
            sorted_df = process_json_data(json_data)
            
            # CSVファイル名に「30年発生確率」を追加して出力（utf-8-sigでエンコードして文字化けを防ぐ）
            output_csv = os.path.join(output_folder, f"{building_name}_30年発生確率.csv")
            sorted_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
            print(f"{building_name}のデータを{output_csv}に保存しました。")

if __name__ == "__main__":
    main()
