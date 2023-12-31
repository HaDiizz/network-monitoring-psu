$(document).ready(function () {
  $("#sla-table").DataTable({
    order: [[0, "asc"]],
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
    searching: true,
  });
  var table = $("#sla-table").DataTable();

  $("#sla-table_filter.dataTables_filter").append($("#slaFilter"));

  var categoryIndex = 0;
  $("#sla-table th").each(function (i) {
    if ($($(this)).html() == "Category") {
      categoryIndex = i;
      return false;
    }
  });

  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    var selectedItem = $("#slaFilter").val();
    var category = data[categoryIndex];
    if (selectedItem === "" || category.includes(selectedItem)) {
      return true;
    }
    return false;
  });

  $("#slaFilter").change(function (e) {
    table.draw();
  });

  table.draw();
});

function openDeleteModal(id, year, category) {
  const modal = document.getElementById("delete_modal");
  modal.querySelector(
    "p"
  ).innerHTML = `คุณยืนยันที่จะลบ <i class="font-bold text-indigo-500">${category} - ${year}</i> ?`;
  const confirmBtn = modal.querySelector("#cf_delete");
  confirmBtn.href = `/admin/service-level-agreement/delete/${id}`;

  modal.showModal();
}

function openEditModal(id, year, ok_status, critical_status, category) {
  const modal = document.getElementById("edit_modal");
  const categoryInput = document.getElementById("edit_category");
  const editYearInput = document.getElementById("edit_year");
  const editIdInput = document.getElementById("edit_sla_config_id");
  const editOkStatusInput = document.getElementById("edit_ok_status");
  const editCriticalStatusInput = document.getElementById(
    "edit_critical_status"
  );
  categoryInput.value = category;
  editYearInput.value = year;
  editIdInput.value = id;
  editOkStatusInput.value = ok_status;
  editCriticalStatusInput.value = critical_status;
  modal.showModal();
}
