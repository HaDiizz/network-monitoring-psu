var osmLayer = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
});

var Esri_WorldImagery = L.tileLayer(
  "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
  {
    maxZoom: 19,
  }
);

var Stadia_AlidadeSmooth = L.tileLayer(
  "https://{s}.tile.jawg.io/jawg-light/{z}/{x}/{y}{r}.png?access-token={accessToken}",
  {
    maxZoom: 19,
    accessToken:
      "LIMUfFvUA0DaZQbkYyYbzSLNFizJ91WY5UzFCxJkDWbC4gETyZcmqwD2OvnXdj6X",
  }
);

defaultMap = L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
  maxZoom: 19,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});
hybridMap = L.tileLayer("http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}", {
  maxZoom: 19,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});

var map = L.map("map", {
  layers: [defaultMap],
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

// Default location value
const latInput = document.getElementById("lat").value;
const lngInput = document.getElementById("lng").value;

const defaultMarker = L.marker([7.008874, 100.498056], {
  icon: redIcon,
  title: "ตำแหน่งที่คุณเลือก",
}).addTo(map);

if (!latInput || !lngInput) {
  document.getElementById("lat").value = 7.008874;
  document.getElementById("lng").value = 100.498056;
} else {
  map.removeLayer(defaultMarker);
}

var marker, zoomed;

map.on("click", handleMapClick);

function updateMarker() {
  const lat = parseFloat(document.getElementById("lat").value);
  const lng = parseFloat(document.getElementById("lng").value);

  map.removeLayer(defaultMarker);

  if (!isNaN(lat) && !isNaN(lng)) {
    if (marker) {
      map.removeLayer(marker);
    }

    marker = L.marker([lat, lng], {
      icon: redIcon,
      title: "ตำแหน่งที่คุณเลือก",
    }).addTo(map);

    map.setView([lat, lng], 18);
  }
}

document.getElementById("lat").addEventListener("change", updateMarker);
document.getElementById("lng").addEventListener("change", updateMarker);

updateMarker();

function handleMapClick(e) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;

  map.removeLayer(defaultMarker);

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

let markers = [];
let markersVisible = false;

function showAllLocations(option) {
  const showButton = document.getElementById("showLocationsButton");

  if (markersVisible) {
    markers.forEach((marker) => map.removeLayer(marker));
    markers = [];
    markersVisible = false;
    showButton.textContent = "แสดงหมุดทั้งหมด";
  } else {
    if (option === "location") {
      fetch("/get-locations")
        .then((response) => response.json())
        .then((data) => {
          if (!data) return;

          data.forEach((location) => {
            var marker = L.marker([location.lat, location.lng], {
              icon: markedIcon,
            }).bindPopup(`${location.name}<br/>`);

            marker.addTo(map);
            markers.push(marker);
          });

          markersVisible = true;
          showButton.textContent = "ซ่อนหมุดทั้งหมด";
        })
        .catch((error) => {
          console.error("Error fetching location data:", error);
        });
    } else if (option === "accessPoint") {
      fetch("/get-ap-locations")
        .then((response) => response.json())
        .then((data) => {
          if (!data) return;

          data.forEach((location) => {
            var marker = L.marker([location.lat, location.lng], {
              icon: markedIcon,
            }).bindPopup(`
            <div class="container">
            <table class="table">
              <thead>
                <tr class="dark:border-[#f2f2f2]">
                  <th class='uppercase'>Properties</th>
                  <th class='uppercase'>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr class="dark:border-[#f2f2f2]">
                  <td>Access Point Name</td>
                  <td>${location.name}</td>
                </tr>
                <tr class="dark:border-[#f2f2f2]">
                  <td>Floor</td>
                  <td>${location.floor ? location.floor : "-"}</td>
                </tr>
                <tr class="dark:border-[#f2f2f2]">
                  <td>Room</td>
                  <td>${location.room ? `${location.room}` : "-"}</td>
                </tr>
              </tbody>
            </table>
          </div>`)
            marker.addTo(map);
            markers.push(marker);
          });

          markersVisible = true;
          showButton.textContent = "ซ่อนหมุดทั้งหมด";
        })
        .catch((error) => {
          console.error("Error fetching location data:", error);
        });
    } else if (option === "host") {
      fetch("/admin/get-host-locations")
        .then((response) => response.json())
        .then((data) => {
          if (!data) return;

          data.forEach((location) => {
            var marker = L.marker([location.lat, location.lng], {
              icon: markedIcon,
            }).bindPopup(`
            <div class="container">
            <table class="table">
              <thead>
                <tr class="dark:border-[#f2f2f2]">
                  <th class='uppercase'>Properties</th>
                  <th class='uppercase'>Value</th>
                </tr>
              </thead>
              <tbody>
                <tr class="dark:border-[#f2f2f2]">
                  <td>Host Name</td>
                  <td>${location.name}</td>
                </tr>
                <tr class="dark:border-[#f2f2f2]">
                  <td>Floor</td>
                  <td>${location.floor ? location.floor : "-"}</td>
                </tr>
                <tr class="dark:border-[#f2f2f2]">
                  <td>Room</td>
                  <td>${location.room ? `${location.room}` : "-"}</td>
                </tr>
              </tbody>
            </table>
          </div>`)
            marker.addTo(map);
            markers.push(marker);
          });

          markersVisible = true;
          showButton.textContent = "ซ่อนหมุดทั้งหมด";
        })
        .catch((error) => {
          console.error("Error fetching location data:", error);
        });
    }
  }
}