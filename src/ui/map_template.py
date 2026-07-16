"""HTML/Leaflet map embedded in the QWebEngineView.

Markers are now pushed from Python as a single JSON payload via
``renderMarkers(quakes)`` instead of one ``addMarker(...)`` string-built JS
call per quake. That removes the old quoting bug (a location name with a
double quote or backslash could break the injected script) and cuts one
network-tick's worth of marker updates from N calls down to 1.
"""
from __future__ import annotations

from config import DEFAULT_CENTER_LAT, DEFAULT_CENTER_LNG, DEFAULT_ZOOM


def get_map_html() -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  html, body, #map {{ width: 100%; height: 100%; margin: 0; padding: 0; background: #1e1f22; }}
  .leaflet-popup-content-wrapper {{ background: #26272b; color: #e8e8ea; border-radius: 8px; }}
  .leaflet-popup-tip {{ background: #26272b; }}
  .eq-popup b {{ font-size: 14px; }}
  .eq-popup .row {{ margin-top: 3px; font-size: 12px; color: #b8b9bd; }}
  .legend {{
    position: absolute; bottom: 20px; right: 10px; z-index: 1000;
    background: rgba(38, 39, 43, 0.85); color: #e8e8ea; padding: 10px 14px;
    border-radius: 8px; font: 12px sans-serif; line-height: 1.7;
    border: 1px solid #3d3e43;
  }}
  .legend .dot {{ display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; }}
</style>
</head>
<body>
<div id="map"></div>
<div class="legend">
  <div><span class="dot" style="background:#e63946"></span>M &ge; 5.0 &mdash; Siddetli</div>
  <div><span class="dot" style="background:#ff9f1c"></span>M &ge; 4.0 &mdash; Yuksek</div>
  <div><span class="dot" style="background:#e8c547"></span>M &ge; 3.0 &mdash; Orta</div>
  <div><span class="dot" style="background:#2ec4b6"></span>M &lt; 3.0 &mdash; Dusuk</div>
</div>
<script>
  var map = L.map('map', {{ zoomControl: true }})
    .setView([{DEFAULT_CENTER_LAT}, {DEFAULT_CENTER_LNG}], {DEFAULT_ZOOM});

  L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
  }}).addTo(map);

  var markerLayer = L.layerGroup().addTo(map);
  var lastQuakes = [];
  var minMagnitude = 0;

  function colorFor(mag) {{
    if (mag >= 5.0) return '#e63946';
    if (mag >= 4.0) return '#ff9f1c';
    if (mag >= 3.0) return '#e8c547';
    return '#2ec4b6';
  }}

  function escapeHtml(text) {{
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }}

  function renderMarkers(quakes) {{
    lastQuakes = quakes;
    markerLayer.clearLayers();
    quakes.forEach(function(q) {{
      if (q.mag < minMagnitude) return;
      var color = colorFor(q.mag);
      var circle = L.circleMarker([q.lat, q.lng], {{
        color: color, fillColor: color, fillOpacity: 0.75, weight: 1,
        radius: Math.max(4, q.mag * 2.6)
      }});
      var safeTitle = escapeHtml(q.title);
      circle.bindPopup(
        '<div class="eq-popup"><b>' + safeTitle + '</b>' +
        '<div class="row">Buyukluk: ' + q.mag.toFixed(1) + '</div>' +
        '<div class="row">Derinlik: ' + q.depth.toFixed(1) + ' km</div>' +
        '<div class="row">Zaman: ' + escapeHtml(q.time) + '</div></div>'
      );
      circle.addTo(markerLayer);
    }});
  }}

  function setMinMagnitude(value) {{
    minMagnitude = value;
    renderMarkers(lastQuakes);
  }}

  function flyTo(lat, lng) {{
    map.flyTo([lat, lng], 10, {{ duration: 1.2 }});
  }}
</script>
</body>
</html>"""
