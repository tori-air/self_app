import folium
import networkx as nx
import osmnx as ox

# 経路探索対象地域を設定
area = ["Morioka,Iwate,Japan"]

# 徒歩のみでグラフを作成
G = ox.graph_from_place(area, network_type="walk")

# 出発地点と到着地点を指定
departure_lat, departure_lon = ox.geocoder.geocode("盛岡駅")
destination_lat, destination_lon = ox.geocoder.geocode("前九年公園")

# 2地点の近似ノードを取得する. 順番は経度､緯度
dep_node = ox.nearest_nodes(G, departure_lon, departure_lat)
des_node = ox.nearest_nodes(G, destination_lon, destination_lat)

# 最短経路探索
shortest_route = ox.shortest_path(G, dep_node, des_node, weight="length")


# 主要道路を避けるためエッジにカスタム重みを設定
def custom_weight_1(U, v, data):
    # 距離情報があるか確認し､ない場合はデフォルト値(1メートル)
    length = data.get("length", 1)
    highway = data.get("highway", "")
    # 狭い道は低コスト
    if highway in ["secondary", "secondary_link"]:
        return length
    # 主要道路は高コスト
    else:
        return length * 10


def custom_weight_2(U, v, data):
    # 距離情報があるか確認し､ない場合はデフォルト値(1メートル)
    length = data.get("length", 1)
    highway = data.get("highway", "")
    # 狭い道は低コスト
    if highway in [
        "residential",
        "service",
        "unclassified",
        "tertiary",
        "living_street",
        "pedestrian",
        "service",
        "track",
    ]:
        return length
    elif highway in ["secondary", "secondary_link"]:
        return length * 20
    # 主要道路は高コスト
    else:
        return length * 100


# カスタム重みを使って経路を計算
backstreet_route_1 = ox.shortest_path(G, dep_node, des_node, weight=custom_weight_1)
backstreet_route_2 = ox.shortest_path(G, dep_node, des_node, weight=custom_weight_2)


# 路線上のエッジごとの所要時間を計算する関数
def calculate_route_travel_time(G, route):
    total_time_sec = 0
    for u, v in zip(route[:-1], route[1:]):
        edge_data = G.get_edge_data(u, v)[0]
        length = edge_data.get("length", 1)  # メートル
        speed_kph = edge_data.get("maxspeed", 30)  # デフォルト速度 30 km/h
        if isinstance(speed_kph, list):
            speed_kph = min(speed_kph)  # リストの場合は最小値を使用
        speed_mps = speed_kph * 1000 / 3600  # km/h を m/s に変換
        travel_time_sec = length / speed_mps  # 時間 = 距離 / 速度
        total_time_sec += travel_time_sec
    return total_time_sec


# 経路の所要時間を計算
shortest_route_time_sec = calculate_route_travel_time(G, shortest_route)
shortest_route_time_min = shortest_route_time_sec / 60  # 分に変換

backstreet_route_1_time_sec = calculate_route_travel_time(G, backstreet_route_1)
backstreet_route_1_time_min = backstreet_route_1_time_sec / 60  # 分に変換

backstreet_route_2_time_sec = calculate_route_travel_time(G, backstreet_route_2)
backstreet_route_2_time_min = backstreet_route_2_time_sec / 60  # 分に変換


# 経路を地図にプロット
# 最短経路
folium_map = ox.plot_route_folium(
    G,
    shortest_route,
    route_map=None,
    color="blue",
    popup_label=f"Shortest Route (Dashed) - Time: {shortest_route_time_min:.2f} minutes",
)

# 中間経路
folium_map = ox.plot_route_folium(
    G,
    backstreet_route_1,
    route_map=folium_map,
    color="green",
    popup_label=f"Backstreet Route 1 (Dashed) - Time: {backstreet_route_1_time_min:.2f} minutes",
)

# 遠方経路
folium_map = ox.plot_route_folium(
    G,
    backstreet_route_2,
    route_map=folium_map,
    color="red",
    popup_lapel=f"Backstreet Route 2 (Dashed) - Time: {backstreet_route_2_time_min:.2f} minutes",
)

# 出発地点と目的地点を地図にマーカーを追加
folium.Marker(location=[departure_lat, departure_lon], icon=folium.Icon(icon="user")).add_to(folium_map)
folium.Marker(location=[destination_lat, destination_lon], icon=folium.Icon(color="red", icon="map-marker")).add_to(folium_map)

# 時間情報を表示するポップアップを追加
folium.Marker(
    location=[departure_lat, departure_lon],
    popup=f"Arrival Time for Backstreet Route 1: {backstreet_route_1_time_min:.2f} minutes",
    icon=folium.Icon(color="green"),
).add_to(folium_map)


folium_map.save("templates/folium_map.html")
