import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Port 5174 so this runs alongside the Day6 app on 5173
export default defineConfig({
  plugins: [react()],
  server: { port: 5174, strictPort: true },
});
