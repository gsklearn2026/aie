/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Google Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      colors: {
        'gcp-blue': '#4285f4',
        'gcp-green': '#34a853',
        'gcp-yellow': '#fbbc04',
        'gcp-red': '#ea4335',
      },
    },
  },
  plugins: [],
}
