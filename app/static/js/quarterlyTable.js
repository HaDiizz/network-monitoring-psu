$(document).ready(function () {
    $("#quarterly-table").DataTable({
      "order": [[0, 'desc']],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "print", "colvis"],
    });
  });
  