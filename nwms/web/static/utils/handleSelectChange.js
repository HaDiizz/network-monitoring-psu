function handleSelectChange() {
  var selectedValue = document.getElementById("ddl-location").value;
  var [lat, lng] = selectedValue.split("|");
  lat = parseFloat(lat);
  lng = parseFloat(lng);
  updateMapView(lat, lng);
}
