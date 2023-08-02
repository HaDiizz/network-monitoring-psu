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

function updateMapView(lat, lng) {
  map.setView([lat, lng], 18);
}

var map = L.map("map", {
  layers: [Stadia_AlidadeSmooth],
}).setView([7.008927, 100.497545], 16);

defaultMap = L.tileLayer("http://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", {
  maxZoom: 19,
  subdomains: ["mt0", "mt1", "mt2", "mt3"],
});
hybridMap = L.tileLayer("http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}", {
  maxZoom: 19,
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

function showHostModal(host) {
  const modal = document.getElementById("host-modal");
  modal.querySelector("#host-title").innerHTML = `${host.title}`;
  modal.querySelector("#host-info-detail").innerHTML = `
  <div class="flex flex-col gap-5">
    <div class="flex-row">
      <span class="font-semibold">Host name</span>
      <span>:</span>
      <span>${host.title}</span>
    </div>
    <div class="flex-row">
      <span class="font-semibold">Host status</span>
      <span>:</span>
      ${
        host.extensions.last_state === 0
          ? "<span>UP</span>"
          : "<span>DOWN</span>"
      }
    </div>
    <div class="flex-row">
      <span class="font-semibold">Connections</span>
      <span>:</span>
      <span>${host.extensions.connected_devices}</span>
    </div>
    <div class="flex-row">
      <span class="font-semibold">Availability</span>
      <span>:</span>
      <span>100%</span>
    </div>
    <div class="flex-row">
      <span class="font-semibold">Floor</span>
      <span>:</span>
      ${host.extensions.attributes.labels.floor ? `<span>${host.extensions.attributes.labels.floor}</span>` : "-"}
      </div>
      <div class="flex-row">
      <span class="font-semibold">Room</span>
      <span>:</span>
      ${host.extensions.attributes.labels.room ? `<span>${host.extensions.attributes.labels.room}</span>` : "-"}
    </div>
  </div>`;
  
  modal.showModal();
}

fetch("/get-hosts")
  .then((response) => response.json())
  .then((data) => {
    data.forEach((host) => {
      var marker = host.extensions.last_state === 1 ? redIcon : greenIcon;
      L.marker(
        [
          host.extensions.attributes.labels.lat,
          host.extensions.attributes.labels.lng,
        ],
        {
          icon: marker,
        }
      )
        .addTo(map)
        .bindPopup(
          `AP Name: ${host.title}<br/> 
          <div class="pt-2 flex justify-center"><a onclick='showHostModal(${JSON.stringify(
            host
          )})' style="text-decoration: none" type="button" class="text-indigo-500 cursor-pointer">
          View Detail
          </a></div>`
        );
    });
  })
  .catch((error) => console.error("Error fetching markers:", error));
