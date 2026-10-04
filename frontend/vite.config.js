import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The "proxy" forwards every /api request to the FastAPI backend.
// That means the browser (and your phone) only ever talks to this one server,
// so there are no CORS or IP-address problems.
export default defineConfig({
  plugins: [react()],
  server: {
    host: true, // also reachable from your phone on the same Wi-Fi
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});