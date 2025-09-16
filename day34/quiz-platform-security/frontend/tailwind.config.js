module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        security: {
          critical: '#dc2626',
          high: '#ea580c',
          medium: '#d97706',
          low: '#65a30d',
          safe: '#16a34a'
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
