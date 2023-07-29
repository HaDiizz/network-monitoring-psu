$(document).ready(function () {
  var table = $("#service-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
  });

  $("#service-table_wrapper div.dataTables_filter").append(
    '<div class="join uppercase p-3 w-100" role="group">' +
      '<button id="btn-filter-up-service" type="button" class="btn join-item filter-btn" data-status="UP"><i class="bx bxs-caret-up-circle text-green-500" style="font-size: 18px"></i><span class="pl-2"> UP</span></button>' +
      '<button id="btn-filter-down" type="button" class="btn join-item filter-btn" data-status="DOWN"><i class="bx bxs-caret-down-circle text-red-500" style="font-size: 18px"></i><span class="pl-2"> DOWN</span></button>' +
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
    if (status === "UP") {
      table.columns(statusColIndex).search("^UP$", true, false).draw();
    } else if (status === "DOWN") {
      table.columns(statusColIndex).search("^DOWN$", true, false).draw();
    }
  });
});
