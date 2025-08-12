(() => {
  'use strict'

  const getStoredTheme = () => localStorage.getItem('theme')
  const setStoredTheme = theme => localStorage.setItem('theme', theme)

  const getPreferredTheme = () => {
    const storedTheme = getStoredTheme()
    if (storedTheme) {
      return storedTheme
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }

  const setTheme = theme => {
    document.documentElement.setAttribute('data-bs-theme', theme)
  }

  setTheme(getPreferredTheme())

  window.addEventListener('DOMContentLoaded', () => {
    const themeSwitcher = document.getElementById('theme-switcher');
    if(themeSwitcher) {
        // Set initial state of the switcher
        const currentTheme = getPreferredTheme();
        if (currentTheme === 'dark') {
            themeSwitcher.checked = true;
        }

        themeSwitcher.addEventListener('change', () => {
            const newTheme = themeSwitcher.checked ? 'dark' : 'light';
            setStoredTheme(newTheme);
            setTheme(newTheme);
        });
    }
  })
})()
