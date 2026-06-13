import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        pitch: {
          900: "#0a1f14",
          800: "#0f2e1d",
          700: "#16633b",
          500: "#1f9d57",
          400: "#34d27f",
        },
      },
    },
  },
  plugins: [],
};

export default config;
