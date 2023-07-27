$(document).ready(function () {
    $("#report-table").DataTable({
      "order": [[0, 'desc']],
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "pdf", "print", "colvis"],
    });
  });
  