import folium

folium_map = folium.Map(location=[39.699657, 141.156873], zoom_start=40)
folium_map = folium.Marker(location=[39.699657, 141.156873], icon=folium.Icon(icon="home")).add_to(folium_map)

folium_map.save("templates/folium_map.html")
