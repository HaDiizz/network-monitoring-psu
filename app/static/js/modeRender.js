var htmlTag = document.getElementsByTagName("html")[0];
const isDarkModeEnabled = localStorage.getItem("darkMode") == "true";
if (isDarkModeEnabled) {
  htmlTag.setAttribute("data-theme", "dark");
} else {
  htmlTag.setAttribute("data-theme", "light");
}
