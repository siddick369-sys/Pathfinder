/* ============================================
   PathFinder — shared.js
   Theme toggle + utility functions
   ============================================ */

// ── Theme Toggle ──
function initTheme() {
    const saved = localStorage.getItem('pathfinder-theme');
    if (saved === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    }
    updateToggleIcon();
}

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next === 'dark' ? 'dark' : '');
    if (next === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        document.documentElement.removeAttribute('data-theme');
    }
    localStorage.setItem('pathfinder-theme', next);
    updateToggleIcon();
}

function updateToggleIcon() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    document.querySelectorAll('.theme-toggle').forEach(btn => {
        btn.innerHTML = isDark ? '☀️' : '🌙';
    });
}

// ── Password toggle ──
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    if (input.type === 'password') {
        input.type = 'text';
    } else {
        input.type = 'password';
    }
}

// ── Smooth scroll ──
function scrollToSection(sectionId) {
    const el = document.getElementById(sectionId);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
}

// ── Init ──
document.addEventListener('DOMContentLoaded', () => {
    initTheme();

    // Attach theme toggle
    document.querySelectorAll('.theme-toggle').forEach(btn => {
        btn.addEventListener('click', toggleTheme);
    });
});
