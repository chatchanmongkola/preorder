/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["Sarabun", "system-ui", "sans-serif"],
      },
      colors: {
        primary: {
          DEFAULT: "#F97316",
          foreground: "#FFFFFF",
        },
        background: "#FFFBF5",
      },
      borderRadius: {
        "2xl": "1rem",
      },
    },
  },
  plugins: [],
};
