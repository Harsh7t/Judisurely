import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        saffron: { DEFAULT: "#FF9933", dark: "#E8850F", light: "#FFB366" },
        india: { green: "#138808", navy: "#000080" },
        legal: { 50: "#FFF8F0", 100: "#FFEDD5", 800: "#9A3412", 900: "#7C2D12" },
      },
      fontFamily: {
        display: ["Georgia", "serif"],
        sans: ["system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
export default config;
