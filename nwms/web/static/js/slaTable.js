$(document).ready(function () {
  $("#sla-table").DataTable({
    order: [[0, "asc"]],
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
  });
});

function openDeleteModal(id, year) {
  const modal = document.getElementById("delete_modal");
  modal.querySelector(
    "p"
  ).innerHTML = `คุณยืนยันที่จะลบ <i class="font-bold text-indigo-500">${year}</i> ?`;
  const confirmBtn = modal.querySelector("#cf_delete");
  confirmBtn.href = `/admin/service-level-agreement/delete/${id}`;

  modal.showModal();
}

function openEditModal(id, year, ok_status, warning_status, critical_status) {
  const modal = document.getElementById("edit_modal");
  const editYearInput = document.getElementById("edit_year");
  const editIdInput = document.getElementById("edit_sla_config_id");
  const editOkStatusInput = document.getElementById("edit_ok_status");
  const editWarningStatusInput = document.getElementById("edit_warning_status");
  const editCriticalStatusInput = document.getElementById(
    "edit_critical_status"
  );
  editYearInput.value = year;
  editIdInput.value = id;
  editOkStatusInput.value = ok_status;
  editWarningStatusInput.value = warning_status;
  editCriticalStatusInput.value = critical_status;
  modal.showModal();
}
