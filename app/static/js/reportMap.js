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
      "kBXuPeAzSz2kY07LD5nLdVPZDTmSpy7x6F0HdWqExLWUgJlqS7L1wWeyRM2lB1dm",
  }
);

var map = L.map("map", {
  layers: [Stadia_AlidadeSmooth],
}).setView([7.008927, 100.497545], 18);

var layerControl = L.control
  .layers({
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

var marker, circle, zoomed;

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
    map.removeLayer(circle);
  }

  marker = L.marker([lat, lng], {
    icon: redIcon,
    title: "ตำแหน่งปัจจุบัน",
  }).addTo(map);
  circle = L.circle([lat, lng], { radius: accuracy }).addTo(map);

  map.setView([lat, lng], 15);

  document.getElementById("lat").value = lat;
  document.getElementById("lng").value = lng;

  if (!zoomed) {
    zoomed = map.fitBounds(circle.getBounds());
  }
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
    map.removeLayer(circle);
  }

  marker = L.marker([lat, lng], {
    icon: redIcon,
    title: "ตำแหน่งที่คุณเลือก",
  }).addTo(map);
  circle = L.circle([lat, lng], { radius: 10 }).addTo(map);

  document.getElementById("lat").value = lat;
  document.getElementById("lng").value = lng;
}
