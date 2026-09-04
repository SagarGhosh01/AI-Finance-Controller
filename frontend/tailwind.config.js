/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        finance: {
          dark: '#0f172a',
          card: '#1e293b',
          border: '#334155',
          primary: '#2563eb',
          accent: '#10b981',
          warning: '#f59e0b',
          danger: '#ef4444',
          subtle: '#64748b'
        }
      }
    },
  },
  plugins: [],
}
