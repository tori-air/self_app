import folium

folium_map = folium.Map(location=[39.699657, 141.156873], zoom_start=15)


folium_map.save("folium_map.html")
