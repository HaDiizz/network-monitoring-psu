$(document).ready(function () {
    $("#category-table").DataTable({
      dom: "Bfrtip",
      buttons: ["copy", "csv", "excel", "print", "colvis"],
    });
  });

  function openDeleteModal(categoryId, categoryName) {
    const modal = document.getElementById("delete_modal");
    modal.querySelector(
      "p"
    ).innerHTML = `คุณยืนยันที่จะลบ <i class="font-bold text-indigo-500">${categoryName}</i> ?`;
    const confirmBtn = modal.querySelector("#cf_delete");
    confirmBtn.href = `/admin/categories/delete/${categoryId}`;
  
    modal.showModal();
  }

  function openEditModal(categoryId, categoryName) {
    const modal = document.getElementById("edit_modal");
    const editCategoryNameInput = document.getElementById('edit_category_name');
    const editCategoryIdInput = document.getElementById('edit_category_id');
    editCategoryNameInput.value = categoryName;
    editCategoryIdInput.value = categoryId;
    modal.showModal();
  }
  