var map = L.map("map", {
  layers: [Stadia_AlidadeSmooth],
}).setView([7.008927, 100.497545], 16);

var baseMapsAP = {
  "Default Map": defaultMap,
  "Hybrid Map": hybridMap,
  OpenStreetMap: osmLayer,
  SatelliteMap: Esri_WorldImagery,
  "Satellite Map": Stadia_AlidadeSmooth,
};

L.control.layers(baseMapsAP).addTo(map);

L.control
  .locate({
    strings: {
      title: "ค้นหาตำแหน่งของคุณ",
      popup: "ตำแหน่งของคุณ",
    },
  })
  .addTo(map);

function updateMapView(lat, lng) {
  map.setView([lat, lng], 18);
}

async function showHostModal(host) {
  const modal = document.getElementById("host-modal");
  const modalInfo = document.getElementById("host-info");
  const host_id = host.host_id;

  await fetch(`/admin/get-host/${host_id}`)
    .then((response) => response.json())
    .then((data) => {
      const graphDiv = document.createElement("div");
      graphDiv.id = "host-plotly-graph";
      modal.querySelector("#host-graph-detail").appendChild(graphDiv);

      const dataGraph = [
        {
          x: data[0],
          y: data[1],
          type: "scatter",
          mode: "lines",
          name: "Host Status",
        },
      ];

      const layout = {
        title: "Host Status",
        xaxis: { title: "Times" },
        yaxis: {
          title: "Status",
          tickvals: [1, 0],
          ticktext: ["UP", "DOWN"],
        },
      };

      Plotly.newPlot("host-plotly-graph", dataGraph, layout);
    });
  modalInfo.style.display = "inherit";
  modal.querySelector("#host-title").innerHTML = `${host.name}`;
  modal.querySelector("#host-info-detail").innerHTML = `
  <div class="container">
  <table class="table">
    <thead>
      <tr>
        <th class='uppercase'>Properties</th>
        <th class='uppercase'>Value</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Host Name</td>
        <td>${host.name}</td>
      </tr>
      <tr>
        <td>Status</td>
        <td>${
          host.state === 0
            ? "<span class='text-green-500 font-bold'>UP</span>"
            : host.state === 1
            ? "<span class='text-red-500 font-bold'>DOWN</span>"
            : "<span class='text-yellow-500 font-bold'>UNREACH</span>"
        }</td>
      </tr>
      <tr>
        <td>Availability</td>
        <td>${host.availability ? `${host.availability} %` : "-"}</td>
      </tr>
    </tbody>
  </table>
</div>`;

  modal.showModal();
}

var markerClusterGroup = L.markerClusterGroup({
  disableClusteringAtZoom: 19,
});

fetch("/admin/get-hosts")
  .then((response) => response.json())
  .then((data) => {
    if (!data) return;
    data.forEach((host) => {
      var marker =
        host.state === 1 ? redIcon : host.state == 0 ? greenIcon : yellowIcon;
      var randomizedLat = host.lat + (Math.random() - 0.5) * 0.00055;
      var randomizedLng = host.lng + (Math.random() - 0.5) * 0.00055;
      var markerData = L.marker([randomizedLat, randomizedLng], {
        icon: marker,
      });

      markerClusterGroup.addLayer(markerData);

      markerData.bindPopup(
        `Host Name: ${host.name}<br/> 
                <div class="pt-2 flex justify-center"><a onclick='showHostModal(${JSON.stringify(
                  host
                )})' style="text-decoration: none" type="button" class="text-indigo-500 cursor-pointer">
                  ดูรายละเอียด
                </a></div>`
      );
    });

    map.addLayer(markerClusterGroup);
  })
  .catch((error) => console.error("Error fetching markers:", error));
