var geolocationWatcher = null;

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
}).setView([7.008927, 100.497545], 18);

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

var marker, zoomed;

var redIcon = L.icon({
  iconUrl: "../static/images/red-mark.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
});

function success(pos) {
  const lat = pos.coords.latitude;
  const lng = pos.coords.longitude;
  const accuracy = pos.coords.accuracy;

  if (marker) {
    map.removeLayer(marker);
  }

  marker = L.marker([lat, lng], {
    icon: redIcon,
    title: "ตำแหน่งปัจจุบัน",
  }).addTo(map);

  map.setView([lat, lng], 15);

  document.getElementById("lat").value = lat;
  document.getElementById("lng").value = lng;
}

function error() {
  alert(
    "Cannot get current location. You can manually mark a location on the map."
  );
  map.on("click", handleMapClick);
}

geolocationWatcher = navigator.geolocation.watchPosition(success, error);

map.on("click", handleMapClick);

function handleMapClick(e) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;

  if (marker) {
    map.removeLayer(marker);
  }

  marker = L.marker([lat, lng], {
    icon: redIcon,
    title: "ตำแหน่งที่คุณเลือก",
  }).addTo(map);

  document.getElementById("lat").value = lat;
  document.getElementById("lng").value = lng;
}
