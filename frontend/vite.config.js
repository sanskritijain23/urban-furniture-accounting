import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Backend runs on :8000 by default (see backend/README section of the
// root README.md). Adjust VITE_API_BASE_URL in frontend/.env instead
// of hardcoding a different port here.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
})
