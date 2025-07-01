// frontend/vite.config.js (or .ts)
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';

export default defineConfig(({ mode }) => {
  // 👇 absolute path to the monorepo root that holds .env
  const envDir = path.resolve(__dirname, '..');

  // Load the correct .env[.mode] file *before* the rest of the config runs
  const env = loadEnv(mode, envDir);

  return {
    // Make the same directory the default for runtime env loading
    envDir,                       // 🔑 <-- this is the missing line
    plugins: [react(), tailwindcss()]
  };
});
