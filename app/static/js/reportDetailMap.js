var mapDiv = document.getElementById("map");
var report = {
  lat: mapDiv.dataset.lat,
  lng: mapDiv.dataset.lng,
};
var osmLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
});

var Esri_WorldImagery = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    maxZoom: 18,
  }
);

var Stadia_AlidadeSmooth = L.tileLayer(
  "https://{s}.tile.jawg.io/jawg-light/{z}/{x}/{y}{r}.png?access-token={accessToken}",
  {
    maxZoom: 18,
    accessToken:
      "LIMUfFvUA0DaZQbkYyYbzSLNFizJ91WY5UzFCxJkDWbC4gETyZcmqwD2OvnXdj6X",
  }
);

defaultMap = L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
  maxZoom: 18,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});
hybridMap = L.tileLayer("http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}", {
  maxZoom: 18,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});

var map = L.map("map", {
  layers: [Stadia_AlidadeSmooth],
}).setView([report.lat, report.lng], 18);

var layerControl = L.control
  .layers({
    DefaultMap: defaultMap,
    HybridMap: hybridMap,
    OpenStreetMap: osmLayer,
    SatelliteMap: Esri_WorldImagery,
    LightMap: Stadia_AlidadeSmooth,
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
