$(document).ready(function () {
  $("#location-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
  });
});
