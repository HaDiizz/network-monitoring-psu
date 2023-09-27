$(document).ready(function () {
    $("#quarterly-table").DataTable({
      "order": [[2, 'desc']],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "print", "colvis"],
    });
  });
  