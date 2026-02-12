/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                slate: {
                    950: '#020617', // Deep dark background
                },
                gold: '#fbbf24',
                silver: '#e2e8f0',
                neon: {
                    green: '#34d399',
                    red: '#f43f5e',
                }
            },
            fontFamily: {
                sans: ['Inter', 'Roboto', 'sans-serif'],
                mono: ['Fira Code', 'monospace'],
            }
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
}
