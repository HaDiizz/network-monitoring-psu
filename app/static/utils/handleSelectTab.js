$(document).ready(function () {
    $(".page-tabs a").click(function () {
      var tab_id = $(this).attr("data-tab");
  
      $(".page-tabs a").removeClass("tab-active");
      $(".page.tab-content").removeClass("current");
  
      $(this).addClass("tab-active");
      $("#" + tab_id).addClass("current");
    });
  });
  