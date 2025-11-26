import { initAuth, checkAuth } from './auth.js';
import { initDashboard } from './dashboard.js';
import { initVault } from './vault.js';

const routes = {
    '#login': { id: 'login-page', init: initAuth },
    '#register': { id: 'register-page', init: initAuth },
    '#dashboard': { id: 'dashboard-page', init: initDashboard, protected: true },
    '#vault': { id: 'vault-page', init: initVault, protected: true },
};

const router = async () => {
    let hash = window.location.hash || '#login';
    if (!routes[hash]) hash = '#login';

    const route = routes[hash];

    if (route.protected && !checkAuth()) {
        return;
    }

    // Toggle Pages
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(route.id).classList.add('active');

    // Toggle Navbar
    const navbar = document.getElementById('navbar');
    if (hash === '#login' || hash === '#register') {
        navbar.classList.add('hidden');
    } else {
        navbar.classList.remove('hidden');
        const user = JSON.parse(localStorage.getItem('user'));
        if (user) {
            document.getElementById('user-display').innerText = user.username;
        }
    }

    // Init Page Logic
    if (route.init) {
        await route.init();
    }
};

window.addEventListener('hashchange', router);
window.addEventListener('load', router);

// Theme Toggle
const themeToggle = document.getElementById('theme-toggle');
themeToggle.addEventListener('click', () => {
    document.documentElement.classList.toggle('dark');
});
