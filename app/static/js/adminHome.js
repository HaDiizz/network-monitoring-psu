$(document).ready(function () {
  var table = $("#host-table").DataTable({
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
    '<div class="join uppercase p-3 w-100" role="group">' +
      '<button id="btn-filter-up" type="button" class="btn join-item filter-btn" data-status="UP"><i class="bx bxs-caret-up-circle text-green-500" style="font-size: 18px"></i><span class="pl-2">UP</span></button>' +
      '<button id="btn-filter-down" type="button" class="btn join-item filter-btn" data-status="DOWN"><i class="bx bxs-caret-down-circle text-red-500" style="font-size: 18px"></i><span class="pl-2">DOWN</span></button>' +
      '<button id="btn-filter-unreach" type="button" class="btn join-item filter-btn" data-status="UNREACH"><i class="bx bxs-info-circle text-yellow-500" style="font-size: 18px"></i><span class="pl-2">UNREACH</span></button>' +
      '<button id="btn-filter-clear" type="button" class="btn join-item clear-btn">CLR</button>' +
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
    if (status === "UP") {
      table.columns(statusColIndex).search("^UP$", true, false).draw();
    } else if (status === "DOWN") {
      table.columns(statusColIndex).search("^DOWN$", true, false).draw();
    } else if (status === "UNREACH") {
      table.columns(statusColIndex).search("^UNREACH$", true, false).draw();
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

  async function showHostModal(host) {
    const modal = document.getElementById("host-modal");
    const modalInfo = document.getElementById("host-info");
    const hostId = host.title;
  
    await fetch(`/get-host/${hostId}`)
      .then((response) => response.json())
      .then((data) => {
        console.log(data); //!  ค่าที่ส่งมาจาก Backend
        const graphDiv = document.createElement("div");
        graphDiv.id = "host-plotly-graph";
        modal.querySelector("#host-graph-detail").appendChild(graphDiv);
  
        const dataGraph = [
          {
            x: data[0],
            y: data[1],
            type: "scatter",
            mode: "lines+markers",
            name: "Host Data",
          },
        ];
  
        const layout = {
          title: "Host Graph",
          xaxis: { title: "X-axis" },
          yaxis: { title: "Y-axis" },
        };
  
        Plotly.newPlot("host-plotly-graph", dataGraph, layout);
      });
    modalInfo.style.display = "inherit";
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
          <span class="font-semibold">Availability</span>
          <span>:</span>
          <span>100%</span>
        </div>
      </div>`;
  
    modal.showModal();
  }

fetch("/get-hosts")
  .then((response) => response.json())
  .then((data) => {
    if (!data) return;
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
          `Host Name: ${host.title}<br/> 
          <div class="pt-2 flex justify-center"><a onclick='showHostModal(${JSON.stringify(
            host
          )})' style="text-decoration: none" type="button" class="text-indigo-500 cursor-pointer">
          ดูรายละเอียด
          </a></div>`
        );
    });
  })
  .catch((error) => console.error("Error fetching markers:", error));

$(document).ready(function () {
  var table = $("#service-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
  });

  $("#service-table_wrapper div.dataTables_filter").append(
    '<div class="join uppercase p-3 w-100" role="group">' +
      '<button id="btn-filter-ok-service" type="button" class="btn join-item filter-btn" data-status="OK"><i class="bx bxs-caret-up-circle text-green-500" style="font-size: 18px"></i><span class="pl-2">OK</span></button>' +
      '<button id="btn-filter-warn" type="button" class="btn join-item filter-btn" data-status="WARN"><i class="bx bxs-caret-down-circle text-yellow-500" style="font-size: 18px"></i><span class="pl-2">WARN</span></button>' +
      '<button id="btn-filter-crit-service" type="button" class="btn join-item filter-btn" data-status="CRIT"><i class="bx bxs-info-circle text-red-500" style="font-size: 18px"></i><span class="pl-2">CRIT</span></button>' +
      '<button id="btn-filter-unknown-service" type="button" class="btn join-item filter-btn" data-status="UNKNOWN"><i class="bx bxs-minus-circle text-neutral-500" style="font-size: 18px"></i><span class="pl-2">UNKNOWN</span></button>' +
      '<button id="btn-filter-clear-service" type="button" class="btn join-item clear-btn">CLR</button>' +
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
    }
  });
});

$(document).ready(function () {
  // $(".modal-tabs a").click(function () {
  //   var tab_id = $(this).attr("data-tab");
  //   $(".modal-tabs a").removeClass("tab-active");
  //   $(".modal-section.tab-content").removeClass("current");

  //   $(this).addClass("tab-active");
  //   $("#" + tab_id).addClass("current");
  // });

  $(".page-tabs a").click(function () {
    var tab_id = $(this).attr("data-tab");

    $(".page-tabs a").removeClass("tab-active");
    $(".page.tab-content").removeClass("current");

    $(this).addClass("tab-active");
    $("#" + tab_id).addClass("current");
  });
});
