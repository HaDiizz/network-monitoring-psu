/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/*", "../templates/layouts/*", "../templates/admin/*", "./js/*"],
  daisyui: {
    themes: ["light", "dark", "black"],
  },
  theme: {
    extend: {
      colors: {
        "base-100": "#1D232A",
        "base-200": "#181c21",
        "dark-primary": "#2A323C",
        "light-primary": "#f9fafb",
        primary: "#003C71",
        secondary: "#456A8D;",
      },
    },
  },
  darkMode: ["class", '[data-theme="dark"]'],
  plugins: [require("daisyui")],
};
