import folium
import osmnx as ox

# 経路探索対象地域を設定
area = ["Morioka,Iwate,Japan"]

# 徒歩のみでグラフを作成
G = ox.graph_from_place(area, network_type="walk")

# 出発地点と到着地点を指定
departure_lat, departure_lon = ox.geocoder.geocode("盛岡駅")
destination_lat, destination_lon = ox.geocoder.geocode("ベアレン醸造所")

# 2地点の近似ノードを取得する
# 順番は経度､緯度
dep_node = ox.nearest_nodes(G, departure_lon, departure_lat)
des_node = ox.nearest_nodes(G, destination_lon, destination_lat)

# 最短経路探索
shortest_route = ox.shortest_path(G, dep_node, des_node)


# 主要道路を避けるためエッジにカスタム重みを設定
def custom_weight(U, v, data):
    # 距離情報があるか確認し､ない場合はデフォルト値(1メートル)
    length = data.get("length", 1)
    highway = data.get("highway", "")
    # 狭い道は低コスト
    if highway in ["residential", "service", "unclassified", "tertiary"]:
        return length
    # 主要道路は高コスト
    else:
        return length * 10


# カスタム重みを使って経路を計算
backstreet_route_1 = ox.shortest_path(G, dep_node, des_node, weight=custom_weight)
backstreet_route_2 = ox.shortest_path(G, dep_node, des_node, weight=custom_weight)


# 経路を地図にプロット
folium_map = ox.plot_route_folium(
    G, shortest_route, route_map=None, popup_label="Shortest Route"
)
folium_map = ox.plot_route_folium(
    G, backstreet_route_1, route_map=folium_map, route_color="green", popup_label="Backstreet Route 1"
)
folium_map = ox.plot_route_folium(
    G, backstreet_route_2, route_map=folium_map, route_color="red", popup_label="Backstreet Route 2"
)

# shortest_route 地図にマーカーを追加
folium.Marker(location=[departure_lat, departure_lon], icon=folium.Icon(icon="user")).add_to(folium_map)
folium.Marker(location=[destination_lat, destination_lon], icon=folium.Icon(color="red", icon="map-marker")).add_to(folium_map)

# backstreet_route_1 地図にマーカーを追加
# folium.Marker(location=[departure_lat, departure_lon], icon=folium.Icon(icon="user")).add_to(folium_map_1)
# folium.Marker(
#     location=[destination_lat, destination_lon], icon=folium.Icon(color="red", icon="map-marker")
# ).add_to(folium_map_1)

# # backstreet_route_2 地図にマーカーを追加
# folium.Marker(location=[departure_lat, departure_lon], icon=folium.Icon(icon="user")).add_to(folium_map_2)
# folium.Marker(
#     location=[destination_lat, destination_lon], icon=folium.Icon(color="red", icon="map-marker")
# ).add_to(folium_map_2)


folium_map.save("templates/folium_map.html")
