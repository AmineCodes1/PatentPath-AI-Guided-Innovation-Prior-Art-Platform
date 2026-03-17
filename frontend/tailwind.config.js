/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        primary: "#003399",
        accent: "#5580C8",
        "risk-high": "#C00000",
        "risk-medium": "#ED7D31",
        "risk-low": "#548235",
        "risk-minimal": "#70AD47",
        surface: "#F5F7FA",
        "text-primary": "#1A1A2E",
        "text-secondary": "#595959",
      },
      boxShadow: {
        panel: "0 10px 30px rgba(0, 51, 153, 0.1)",
      },
    },
  },
  plugins: [],
};
