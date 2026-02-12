// Save this as Myportfolio/Version 2/theme-engine.js
function applyTheme(themeName) {
    document.body.className = document.body.className.replace(/theme-\S+/g, '').trim();
    document.body.classList.add(themeName);
    localStorage.setItem('theme', themeName);
    
    // Dispatch a custom event so specific pages (like those with canvases) can react
    window.dispatchEvent(new CustomEvent('themeChanged', { detail: themeName }));
}

document.addEventListener('DOMContentLoaded', () => {
    const themeToggleButton = document.getElementById('theme-toggle-btn');
    const themeOptionsMenu = document.getElementById('theme-options-menu');
    const themeOptionButtons = document.querySelectorAll('.theme-option-btn');

    const savedTheme = localStorage.getItem('theme') || 'theme-lucid-blue';
    applyTheme(savedTheme);

    if (themeToggleButton) {
        themeToggleButton.addEventListener('click', (e) => {
            e.stopPropagation();
            themeOptionsMenu.classList.toggle('visible');
        });
    }

    themeOptionButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            applyTheme(btn.dataset.theme);
            themeOptionsMenu.classList.remove('visible');
        });
    });

    window.addEventListener('click', () => themeOptionsMenu?.classList.remove('visible'));
});