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
      "kBXuPeAzSz2kY07LD5nLdVPZDTmSpy7x6F0HdWqExLWUgJlqS7L1wWeyRM2lB1dm",
  }
);

function updateMapView(lat, lng) {
  map.setView([lat, lng], 18);
}

var map = L.map("map", {
  layers: [Stadia_AlidadeSmooth],
}).setView([7.008927, 100.497545], 16);

defaultMap = L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
  maxZoom: 18,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});
hybridMap = L.tileLayer("http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}", {
  maxZoom: 18,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});

var layerControl = L.control
  .layers({
    DefaultMap: defaultMap,
    HybridMap: hybridMap,
    OpenStreetMap: osmLayer,
    SatelliteMap: Esri_WorldImagery,
    LightMap: Stadia_AlidadeSmooth,
  })
  .addTo(map);

L.control
  .locate({
    strings: {
      title: "ค้นหาตำแหน่งของคุณ",
      popup: "ตำแหน่งของคุณ",
    },
  })
  .addTo(map);
