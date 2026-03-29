/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#f7f9fb",
        primary: "#000000",
        secondary: "#006e2f",
        "surface": "#f7f9fb",
        "surface-variant": "#e0e3e5",
        "surface-container": "#eceef0",
        "surface-container-low": "#f2f4f6",
        "surface-container-high": "#e6e8ea",
        "surface-container-highest": "#e0e3e5",
        "surface-container-lowest": "#ffffff",
        "primary-container": "#131b2e",
        "secondary-container": "#6bff8f",
        "tertiary-container": "#410004",
        "on-primary": "#ffffff",
        "on-secondary": "#ffffff",
        "on-background": "#191c1e",
        "on-surface": "#191c1e",
        "on-surface-variant": "#45464d",
        "on-primary-container": "#7c839b",
        "on-secondary-container": "#007432",
        "on-tertiary-container": "#ef4444",
        "error": "#ba1a1a",
        "error-container": "#ffdad6",
        "outline": "#76777d",
        "outline-variant": "#c6c6cd",
      },
    },
  },
  plugins: [],
}
