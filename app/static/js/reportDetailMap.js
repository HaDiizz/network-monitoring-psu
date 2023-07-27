var mapDiv = document.getElementById("map");
var report = {
  lat: mapDiv.dataset.lat,
  lng: mapDiv.dataset.lng,
};
var osmLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
});

var Esri_WorldImagery = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {}
);

var Stadia_AlidadeSmooth = L.tileLayer(
  "https://tiles.stadiamaps.com/tiles/alidade_smooth/{z}/{x}/{y}{r}.png",
  {
    maxZoom: 20,
  }
);

var map = L.map("map", {
  layers: [Stadia_AlidadeSmooth],
}).setView([report.lat, report.lng], 15);

var layerControl = L.control
  .layers({
    OpenStreetMap: osmLayer,
    SatelliteImagery: Esri_WorldImagery,
    TopographicMap: Stadia_AlidadeSmooth,
  })
  .addTo(map);

var marker;

var redIcon = L.icon({
  iconUrl: "../../static/images/red-mark.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

marker = L.marker([report.lat, report.lng], {
  icon: redIcon,
}).addTo(map);
