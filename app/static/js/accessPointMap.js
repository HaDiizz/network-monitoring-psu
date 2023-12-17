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
            <div class="flex flex-col gap-5">
              <div class="flex-row">
                <span class="font-semibold">AP name</span>
                <span>:</span>
                <span>${ap.name}</span>
              </div>
              <div class="flex-row">
                <span class="font-semibold">AP status</span>
                <span>:</span>
                ${ap.state === 0 ? "<span>UP</span>" : "<span>DOWN</span>"}
              </div>
              <div class="flex-row">
                <span class="font-semibold">Availability</span>
                <span>:</span>
                <span>-</span>
              </div>
            </div>`;

  modal.showModal();
}

var markerClusterGroup = L.markerClusterGroup();

fetch("/get-aps")
  .then((response) => response.json())
  .then((data) => {
    if (!data) return;
    data.forEach((ap) => {
      var marker =
        ap.state === 2 ? redIcon : ap.state == 0 ? greenIcon : yellowIcon;
      var markerData = L.marker([ap.lat, ap.lng], { icon: marker });

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
