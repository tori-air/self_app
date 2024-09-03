import folium
import osmnx as ox

# 経路探索対象地域を設定
area = ["Morioka,Iwate,Japan"]

# 徒歩のみでグラフを作成
G = ox.graph_from_place(area, network_type="walk")

# 出発地点と到着地点を指定
# departure = (39.701437, 141.136723)
# destination = (39.699657, 141.156873)
departure_lat, departure_lon = ox.geocoder.geocode("岩手県庁")
destination_lat, destination_lon = ox.geocoder.geocode("盛岡駅")

# 2地点の近似ノードを取得する
# 順番は経度､緯度
dep_node = ox.nearest_nodes(G, departure_lon, departure_lat)
des_node = ox.nearest_nodes(G, destination_lon, destination_lat)

# 最短経路探索
shortest_route = ox.shortest_path(G, dep_node, des_node)

# # 経路を地図にプロット
folium_map = ox.plot_route_folium(G, shortest_route)
# folium_map = folium.Map(location=[departure_lat, departure_lon], zoom_start=30)
# folium_map = folium.Map(location=[destination_lat, destination_lon], zoom_start=30)

# 地図にマーカーを追加
folium.Marker(location=[departure_lat, departure_lon]).add_to(folium_map)
folium.Marker(location=[destination_lat, destination_lon]).add_to(folium_map)

folium_map.save("templates/folium_map.html")
