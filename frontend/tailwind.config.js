/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f8f9ff',
          100: '#e8eaff',
          200: '#d1d4ff',
          300: '#a7adff',
          400: '#7c84ff',
          500: '#5158ff',
          600: '#2f37ff',
          700: '#0008eb',
          800: '#0006bd',
          900: '#00058f',
        },
      },
      fontFamily: {
        sans: ['Inter var', 'sans-serif'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
