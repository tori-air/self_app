from flask import Flask, render_template, request
import folium
import osmnx as ox

# キャッシュの無効化
ox.config(use_cache=False)

app = Flask(__name__)


@app.route("/foliummap")
def foliummap():
    # 経路探索対象地域を設定
    area = ["Morioka,Iwate,Japan"]

    # 徒歩のみでグラフを作成
    G = ox.graph_from_place(area, network_type="walk")

    # 出発地点と到着地点を指定
    departure_lat, departure_lon = ox.geocoder.geocode("岩手県庁")
    destination_lat, destination_lon = ox.geocoder.geocode("岩手大学")

    # 2地点の近似ノードを取得する. 順番は経度､緯度
    dep_node = ox.nearest_nodes(G, departure_lon, departure_lat)
    des_node = ox.nearest_nodes(G, destination_lon, destination_lat)

    # 最短経路探索
    shortest_route = ox.shortest_path(G, dep_node, des_node, weight="length")

    # 主要道路を避けるためエッジにカスタム重みを設定
    def custom_weight_1(u, v, data):
        length = data.get("length", 1)  # 距離情報（m）
        highway = data.get("highway", "")
        natural = data.get("natural", "")
        leisure = data.get("leisure", "")
        # 散策路や川沿いを優先する
        if highway in ["path", "pedestrian", "footway", "cycleway"]:
            return length * 0.5  # コストを半分にして優先する
        # 'riverbank', 'waterway' などで川沿いのエリアを優先
        if natural in ["water", "wetland"]:
            return length * 0.7  # 川沿いの道は少し優先
        if leisure in ["park", "nature_reserve"]:
            return length * 0.7  # 公園や自然保護区も優先
        # 主要道路はコストを大きくして避ける
        if highway in ["primary", "secondary", "primary_link", "secondary_link"]:
            return length * 10
        # 他の道路は通常通り
        else:
            return length

    def custom_weight_2(x, y, data):
        length = data.get("length", 1)  # 距離情報（m）
        highway = data.get("highway", "")
        landuse = data.get("landuse", "")
        amenity = data.get("amenity", "")
        shop = data.get("shop", "")
        # 古い通りや商店街を優先する
        if highway in ["residential", "unclassified", "tertiary", "tertiary_link"]:
            return length * 0.7  # 住宅街やローカルな通りはコストを下げて優先
        if landuse in ["commercial", "retail"]:
            return length * 0.5  # 商業地区や商店街を優先
        if shop or amenity:  # 店や施設があるエリアを優先
            return length * 0.5  # 商業施設や商店街のルートを優先
        # 他の道路は通常通り
        else:
            return length

    # カスタム重みを使って経路を計算
    backstreet_route_1 = ox.shortest_path(G, dep_node, des_node, weight=custom_weight_1)
    backstreet_route_2 = ox.shortest_path(G, dep_node, des_node, weight=custom_weight_2)

    # 路線上のエッジごとの所要時間を計算する関数
    # def calculate_route_travel_time(G, route):
    #     total_time_sec = 0
    #     for u, v in zip(route[:-1], route[1:]):
    #         edge_data = G.get_edge_data(u, v)[0]
    #         length = edge_data.get("length", 1)  # メートル
    #         speed_kph = edge_data.get("maxspeed", 5)  # デフォルト速度 30 km/h
    #         if isinstance(speed_kph, list):
    #             speed_kph = min(speed_kph)  # リストの場合は最小値を使用
    #         speed_mps = speed_kph * 1000 / 3600  # km/h を m/s に変換
    #         travel_time_sec = length / speed_mps  # 時間 = 距離 / 速度
    #         total_time_sec += travel_time_sec
    #     return total_time_sec

    # 経路の所要時間を計算
    # shortest_route_time_sec = calculate_route_travel_time(G, shortest_route)
    # shortest_route_time_min = shortest_route_time_sec / 60  # 分に変換

    # backstreet_route_1_time_sec = calculate_route_travel_time(G, backstreet_route_1)
    # backstreet_route_1_time_min = backstreet_route_1_time_sec / 60  # 分に変換

    # backstreet_route_2_time_sec = calculate_route_travel_time(G, backstreet_route_2)
    # backstreet_route_2_time_min = backstreet_route_2_time_sec / 60  # 分に変換

    # 経路を地図にプロット
    folium_map = ox.plot_route_folium(
        G,
        shortest_route,
        route_map=None,
        color="blue"
    )

    folium_map = ox.plot_route_folium(
        G,
        backstreet_route_1,
        route_map=folium_map,
        color="green"
    )

    folium_map = ox.plot_route_folium(
        G,
        backstreet_route_2,
        route_map=folium_map,
        color="red"
    )

    # 出発地点と目的地点を地図にマーカーを追加
    folium.Marker(location=[departure_lat, departure_lon], icon=folium.Icon(icon="user"), popup="START").add_to(folium_map)
    folium.Marker(location=[destination_lat, destination_lon], icon=folium.Icon(color="red", icon="map-marker"), popup="GOAL").add_to(folium_map)

    # 時間情報を表示するポップアップを追加
    # ポップアップを手動で追加
    # folium.Marker(
    #     location=[departure_lat, departure_lon],
    #     popup=f"Shortest Route - Time: {shortest_route_time_min:.2f} minutes",
    #     icon=folium.Icon(color="blue"),
    # ).add_to(folium_map)

    # folium.Marker(
    #     location=[departure_lat, departure_lon],
    #     popup=f"Backstreet Route 1 - Time: {backstreet_route_1_time_min:.2f} minutes",
    #     icon=folium.Icon(color="green"),
    # ).add_to(folium_map)

    # folium.Marker(
    #     location=[departure_lat, departure_lon],
    #     popup=f"Backstreet Route 2 - Time: {backstreet_route_2_time_min:.2f} minutes",
    #     icon=folium.Icon(color="red"),
    # ).add_to(folium_map)

    folium_map.save("templates/map.html")
    return render_template("folium_map.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
