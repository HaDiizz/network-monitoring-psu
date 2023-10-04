function handleExpand() {
  var layoutContainer = document.getElementById("layoutContainer");
  var mapContainer = document.getElementById("mapContainer");
  var elementContainer = document.getElementById("elementContainer");
  const tableHeader = document.querySelector(".dataTables_scrollHeadInner");
  const tableElement = document.querySelector(".display.dataTable.no-footer");
  if (mapContainer.classList.contains("expanded")) {
    mapContainer.classList.remove("expanded");
    layoutContainer.classList.remove("lg:flex-col");
    layoutContainer.classList.add("lg:flex-row");
    layoutContainer.classList.remove("md:flex-col");
    layoutContainer.classList.add("md:flex-row");
    mapContainer.classList.remove("md:w-12/12");
    mapContainer.classList.add("md:w-7/12");
    elementContainer.classList.remove("md:w-12/12");
    elementContainer.classList.add("md:w-5/12");
    if (tableHeader) {
      tableHeader.style.width = "455.05px";
      tableElement.style.width = "455.05px";
    }
  } else {
    mapContainer.classList.add("expanded");
    layoutContainer.classList.remove("lg:flex-row");
    layoutContainer.classList.add("lg:flex-col");
    layoutContainer.classList.remove("md:flex-row");
    layoutContainer.classList.add("md:flex-col");
    mapContainer.classList.remove("md:w-7/12");
    mapContainer.classList.add("md:w-12/12");
    elementContainer.classList.remove("md:w-5/12");
    elementContainer.classList.add("md:w-12/12");
    if (tableHeader) {
      tableHeader.style.width = "1146px";
      tableElement.style.width = "1146px";
    }
  }
  map.invalidateSize();
}
