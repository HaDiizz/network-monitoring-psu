$(document).ready(function () {
  $("#location-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
  });
});

function openDeleteModal(locationId, locationName) {
  const modal = document.getElementById("delete_modal");
  modal.querySelector(
    "p"
  ).innerHTML = `คุณยืนยันที่จะลบ <i class="font-bold text-indigo-500">${locationName}</i> ?`;
  const confirmBtn = modal.querySelector("#cf_delete");
  confirmBtn.href = `/admin/locations/delete/${locationId}`;

  modal.showModal();
}
