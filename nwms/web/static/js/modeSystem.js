var htmlTag = document.getElementsByTagName("html")[0];
const isDarkModeEnabled = localStorage.getItem("darkMode") == "true";
if (isDarkModeEnabled) {
  htmlTag.setAttribute("data-theme", "dark");
} else {
  htmlTag.setAttribute("data-theme", "light");
}

window.onload = function () {
  const toggle = document.querySelector("#toggle");
  if (localStorage.darkMode === "true" || localStorage.darkMode === 1) {
    document.documentElement.setAttribute("data-theme", "dark");
    document.getElementById("toggle").checked = true;
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    document.getElementById("toggle").checked = false;
  }

  toggle.addEventListener("change", () => {
    document.documentElement.classList.toggle("dark");
    document.documentElement.classList.toggle("light");
    localStorage.darkMode = toggle.checked ? "true" : "false";
    document.documentElement.setAttribute(
      "data-theme",
      toggle.checked ? "dark" : "light"
    );

    if (toggle.checked) {
      document.documentElement.classList.remove("light");
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
      document.documentElement.classList.add("light");
    }
  });
};
