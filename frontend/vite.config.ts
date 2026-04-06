import { defineConfig } from "vite";

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      "/api": `http://localhost:${process.env.KB_PORT || 5002}`,
    },
  },
});
