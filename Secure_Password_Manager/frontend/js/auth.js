import { api } from './api.js';
import { showToast } from './utils.js';

export const initAuth = () => {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const logoutBtn = document.getElementById('logout-btn');

    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(loginForm);
            const data = Object.fromEntries(formData.entries());

            try {
                const response = await api.post('/auth/login', data);
                localStorage.setItem('access_token', response.access_token);
                localStorage.setItem('user', JSON.stringify(response.user));
                showToast('Login successful');
                window.location.hash = '#dashboard';
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
    }

    if (registerForm) {
        registerForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(registerForm);
            const data = Object.fromEntries(formData.entries());

            if (data.password !== data.confirmPassword) {
                showToast('Passwords do not match', 'error');
                return;
            }

            try {
                await api.post('/auth/register', {
                    username: data.username,
                    password: data.password
                });
                showToast('Registration successful! Please login.');
                window.location.hash = '#login';
            } catch (error) {
                showToast(error.message, 'error');
            }
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await api.post('/auth/logout');
            } catch (e) {
                console.error(e);
            }
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            window.location.hash = '#login';
        });
    }
};

export const checkAuth = () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
        const hash = window.location.hash;
        if (hash !== '#login' && hash !== '#register') {
            window.location.hash = '#login';
        }
        return false;
    }
    return true;
};
