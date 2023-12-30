$(document).ready(function () {
  $("#location-table").DataTable({
    dom: "Bfrtip",
    buttons: ["copy", "csv", "excel", "print", "colvis"],
  });
});

function openDeleteModal(item_id, item_name, option) {
  const modal = document.getElementById("delete_modal");
  modal.querySelector(
    "p"
  ).innerHTML = `คุณยืนยันที่จะลบ <i class="font-bold text-indigo-500">${item_name}</i> ?`;
  const confirmBtn = modal.querySelector("#cf_delete");
  if (option === "location") {
    confirmBtn.href = `/admin/locations/delete/${item_id}`;
  } else if (option === "accessPoint") {
    confirmBtn.href = `/admin/access-point-location/delete/${item_id}`;
  } else if (option === "host") {
    confirmBtn.href = `/admin/host-location/delete/${item_id}`;
  }

  modal.showModal();
}
