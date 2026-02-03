# ui/map_template.py

def get_map_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
        <style>
            body, html, #map {width: 100%; height: 100%; margin: 0; padding: 0; background: #2b2b2b;}
            .leaflet-popup-content-wrapper {background: #333; color: #fff;}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([39.0, 35.0], 6);
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
                attribution: 'OpenStreetMap & CartoDB',
                subdomains: 'abcd',
                maxZoom: 19
            }).addTo(map);

            var markers = [];

            function clearMarkers() {
                markers.forEach(function(marker) { map.removeLayer(marker); });
                markers = [];
            }

            function addMarker(lat, lng, title, mag) {
                var color = mag >= 4.0 ? '#ff3333' : (mag >= 3.0 ? '#ff9900' : '#33cc33');
                var radius = mag * 2.5;

                var circle = L.circleMarker([lat, lng], {
                    color: color, fillColor: color, fillOpacity: 0.7, weight: 1, radius: radius
                }).addTo(map);

                circle.bindPopup("<b>" + title + "</b><br>Büyüklük: " + mag);
                markers.push(circle);
            }

            function flyTo(lat, lng) {
                map.flyTo([lat, lng], 10, {duration: 1.5});
            }
        </script>
    </body>
    </html>
    """
