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
}).setView([7.008927, 100.497545], 15);

var layerControl = L.control
  .layers({
    OpenStreetMap: osmLayer,
    SatelliteImagery: Esri_WorldImagery,
    TopographicMap: Stadia_AlidadeSmooth,
  })
  .addTo(map);

  L.control.locate({
    strings: {
      title: "ค้นหาตำแหน่งของคุณ",
      popup: "ตำแหน่งของคุณ"
    },
  }).addTo(map);
