$(document).ready(function () {
  var table = $("#accessPoint-table").DataTable({
    dom: "lfrtipB",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
    pageSize: 5,
    paging: true,
    lengthMenu: [
      [5, 10, 25, 50, 100, -1],
      [5, 10, 25, 50, 100, "All"],
    ],
    scrollCollapse: true,
    scrollY: "230px",
  });

  $("div.dataTables_filter").append(
    '<div id="btn_filter_groups" class="join uppercase p-1 w-100" role="group">' +
      '<button id="btn-filter-ok-ap" type="button" class="btn join-item filter-btn" data-status="OK"><i class="bx bxs-caret-up-circle text-green-500" style="font-size: 18px"></i><span class="pl-2">OK</span></button>' +
      '<button id="btn-filter-warn-ap" type="button" class="btn join-item filter-btn" data-status="WARN"><i class="bx bxs-info-circle text-yellow-500" style="font-size: 18px"></i><span class="pl-2">WARN</span></button>' +
      '<button id="btn-filter-crit-ap" type="button" class="btn join-item filter-btn" data-status="CRIT"><i class="bx bxs-caret-down-circle text-red-500" style="font-size: 18px"></i><span class="pl-2">CRIT</span></button>' +
      '<button id="btn-filter-unknown-ap" type="button" class="btn join-item filter-btn" data-status="UNKNOWN"><i class="bx bxs-minus-circle text-indigo-500" style="font-size: 18px"></i><span class="pl-2">UNKNOWN</span></button>' +
      '<button id="btn-filter-maintain" type="button" class="btn join-item filter-btn" data-status="MAINTAIN"><i class="bx bxs-traffic-cone text-neutral-500" style="font-size: 18px"></i><span class="pl-2">MAINTAIN</span></button>' +
      '<button id="btn-filter-clear-ap" type="button" class="btn join-item clear-btn">CLR</button>' +
      "</div>"
  );
  var statusColIndex = table
    .columns()
    .header()
    .toArray()
    .findIndex(function (el) {
      return $(el).text() === "Status";
    });
  $(".clear-btn").on("click", function () {
    table.columns().search("").draw();
  });
  $(".filter-btn").on("click", function () {
    var status = $(this).data("status");
    if (status === "OK") {
      table.columns(statusColIndex).search("^OK$", true, false).draw();
    } else if (status === "WARN") {
      table.columns(statusColIndex).search("^WARN$", true, false).draw();
    } else if (status === "CRIT") {
      table.columns(statusColIndex).search("^CRIT$", true, false).draw();
    } else if (status === "UNKNOWN") {
      table.columns(statusColIndex).search("^UNKNOWN$", true, false).draw();
    } else if (status === "MAINTAIN") {
      table.columns(statusColIndex).search("^MAINTAIN$", true, false).draw();
    }
  });
});
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
                : "<span class='text-indigo-500 font-bold'>UNKNOWN</span>"
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
    data.forEach((ap, index) => {
      var marker =
        ap.state === 2
          ? redIcon
          : ap.state == 0
          ? greenIcon
          : ap.state == 1
          ? yellowIcon
          : indigoIcon;
      // var randomizedLat = ap.lat + (Math.random() - 0.5) * 0.00055;
      // var randomizedLng = ap.lng + (Math.random() - 0.5) * 0.00055;
      // var markerData = L.marker([randomizedLat, randomizedLng], {
      //   icon: marker,
      // });
      var markerData = L.marker([ap.lat, ap.lng], {
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
