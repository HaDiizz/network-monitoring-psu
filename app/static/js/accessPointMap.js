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

async function showAPModal(ap) {
  const modal = document.getElementById("ap-modal");
  const modalInfo = document.getElementById("ap-info");
  const accessPoint_id = ap.accessPoint_id;

  await fetch(`/get-ap/${accessPoint_id}`)
    .then((response) => response.json())
    .then((data) => {
      const graphDiv = document.createElement("div");
      graphDiv.id = "ap-plotly-graph";
      modal.querySelector("#ap-graph-detail").appendChild(graphDiv);

      const dataGraph = [
        {
          x: data[0],
          y: data[1],
          type: "scatter",
          mode: "lines",
          name: "AP Status",
        },
      ];

      const layout = {
        title: "AP Status",
        xaxis: { title: "Times" },
        yaxis: {
          title: "Status",
          tickvals: [1, 0],
          ticktext: ["UP", "DOWN"],
        },
      };

      Plotly.newPlot("ap-plotly-graph", dataGraph, layout);
    });
  modalInfo.style.display = "inherit";
  modal.querySelector("#ap-title").innerHTML = `${ap.name}`;
  modal.querySelector("#ap-info-detail").innerHTML = `
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
            <td>Access Point Name</td>
            <td>${ap.name}</td>
          </tr>
          <tr>
            <td>Status</td>
            <td>${
              ap.state === 0
                ? "<span class='text-green-500 font-bold'>OK</span>"
                : ap.state === 1
                ? "<span class='text-yellow-500 font-bold'>WARN</span>"
                : ap.state === 2
                ? "<span class='text-red-500 font-bold'>CRIT</span>"
                : "<span class='text-neutral-500 font-bold'>UNKNOWN</span>"
            }</td>
          </tr>
          <tr>
            <td>Availability</td>
            <td>${ap.availability ? `${ap.availability} %` : "-"}</td>
          </tr>
        </tbody>
      </table>
    </div>`;

  modal.showModal();
}

var markerClusterGroup = L.markerClusterGroup({
  disableClusteringAtZoom: 19,
});

fetch("/get-aps")
  .then((response) => response.json())
  .then((data) => {
    if (!data) return;
    data.forEach((ap) => {
      var marker =
        ap.state === 2
          ? redIcon
          : ap.state == 0
          ? greenIcon
          : ap.state == 1
          ? yellowIcon
          : slateIcon;
      var randomizedLat = ap.lat + (Math.random() - 0.5) * 0.00055;
      var randomizedLng = ap.lng + (Math.random() - 0.5) * 0.00055;
      var markerData = L.marker([randomizedLat, randomizedLng], {
        icon: marker,
      });

      markerClusterGroup.addLayer(markerData);

      markerData.bindPopup(
        `AP Name: ${ap.name}<br/> 
                <div class="pt-2 flex justify-center"><a onclick='showAPModal(${JSON.stringify(
                  ap
                )})' style="text-decoration: none" type="button" class="text-indigo-500 cursor-pointer">
                  ดูรายละเอียด
                </a></div>`
      );
    });

    map.addLayer(markerClusterGroup);
  })
  .catch((error) => console.error("Error fetching markers:", error));
