$(document).ready(function () {
    $("#category-table").DataTable({
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "print", "colvis"],
    });
  });