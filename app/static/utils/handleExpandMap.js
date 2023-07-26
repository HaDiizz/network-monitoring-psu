function handleExpand() {
  var layoutContainer = document.getElementById("layoutContainer");
  var mapContainer = document.getElementById("mapContainer");
  var elementContainer = document.getElementById("elementContainer");

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
  }
  map.invalidateSize();
}
