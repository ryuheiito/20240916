import pandas as pd
from geopy.geocoders import Nominatim
import requests
from bs4 import BeautifulSoup
import os
import time

# 住所を「県（province）」と「市」まで取得する関数
def get_prefecture_city_from_latlon(lat, lon):
    geolocator = Nominatim(user_agent="my_unique_app_name")  # 固有のuser_agentに設定
    try:
        location = geolocator.reverse(f"{lat}, {lon}", language="ja")
        time.sleep(3)  # 各リクエスト間に3秒の遅延を追加
        
        if location:
            address = location.raw['address']
            print(f"Raw address data: {address}")  # デバッグ用に取得した住所を表示

            prefecture = address.get('province', '') or address.get('state', '') or address.get('region', '')
            city = address.get('city', '') or address.get('town', '') or address.get('village', '') or address.get('county', '')
            return f"{prefecture} {city}".strip() if prefecture and city else None
        else:
            return None
    except Exception as e:
        print(f"Error retrieving address for lat={lat}, lon={lon}: {e}")
        return None

# ウェブ検索と結果取得の関数
def search_map_urls(query):
    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    results = []
    for item in soup.find_all('div', class_='tF2Cxc'):
        a_tag = item.find('a', href=True)
        if a_tag and len(results) < 3:
            title = a_tag.text
            url = a_tag['href']
            results.append((title, url))
    return results

# ファイル読み込みと処理
def process_latlon_file(input_file, output_folder):
    df = pd.read_excel(input_file)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_data = []

    for index, row in df.iterrows():
        lat = row['緯度']
        lon = row['経度']
        building_name = row['建物名']
        
        address = get_prefecture_city_from_latlon(lat, lon)
        print(f"Address for {building_name}: {address}")
        
        if address:
            queries = [
                f"{address} ゆれやすさマップ",
                f"{address} 地震ハザードマップ",
                f"{address} 液状化危険度マップ",
                f"{address} 浸水想定区域図",
                f"{address} 内水氾濫"
            ]
            
            for query in queries:
                print(f"\n検索クエリ: {query}")
                results = search_map_urls(query)
                
                for title, url in results:
                    print(f"タイトル: {title}\nURL: {url}")
                    output_data.append({
                        "建物名": building_name,
                        "住所": address,
                        "検索クエリ": query,
                        "タイトル": title,
                        "URL": url
                    })

    # 結果を1つのCSVファイルに保存
    output_file = os.path.join(output_folder, "参考資料.csv")
    output_df = pd.DataFrame(output_data)
    output_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"Results saved to {output_file}")

# 実行部分
input_file = "input/latlon.xlsx"
output_folder = "output"
process_latlon_file(input_file, output_folder)
