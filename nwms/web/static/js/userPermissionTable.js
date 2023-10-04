$(document).ready(function () {
  $("#user-table").DataTable({
    order: [[3, "asc"]],
  });
  $(".role-toggle").on("click", function () {
    var userId = $(this).data("user-id");
    var isAdmin = $(this).prop("checked");
    $.ajax({
      url: "/admin/permission",
      method: "POST",
      data: {
        user_id: userId,
        is_admin: isAdmin,
      },
      success: function (response) {
        var roleBadge = $("#user-role-" + userId)
          .parent()
          .prev()
          .find(".badge");
        if (isAdmin) {
          roleBadge
            .removeClass("badge-success")
            .addClass("badge-error")
            .text("ผู้ดูแลระบบ");
        } else {
          roleBadge
            .removeClass("badge-error")
            .addClass("badge-success")
            .text("ผู้ใช้");
        }
      },
      error: function (error) {},
    });
  });
});
