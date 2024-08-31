import folium

folium_map = folium.Map(location=[39.701437, 141.136723], zoom_start=15)


folium_map.save("folium_map.html")
