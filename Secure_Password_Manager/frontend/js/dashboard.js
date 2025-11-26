import { api } from './api.js';

export const initDashboard = async () => {
    try {
        const passwords = await api.get('/passwords');

        const total = passwords.length;
        const weak = passwords.filter(p => p.password.length < 10).length;
        const favorites = passwords.filter(p => p.favorite).length;
        const unique = new Set(passwords.map(p => p.password)).size;
        const reused = total - unique;
        const score = total > 0 ? Math.max(0, 100 - (weak * 10) - (reused * 5)) : 0;

        const statsContainer = document.getElementById('stats-container');
        statsContainer.innerHTML = `
            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <div>
                    <p class="text-sm font-medium text-gray-500">Total Passwords</p>
                    <h3 class="text-3xl font-bold mt-2">${total}</h3>
                </div>
                <div class="p-3 rounded-lg bg-blue-500"><i data-lucide="key" class="text-white"></i></div>
            </div>
            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <div>
                    <p class="text-sm font-medium text-gray-500">Security Score</p>
                    <h3 class="text-3xl font-bold mt-2">${score}%</h3>
                </div>
                <div class="p-3 rounded-lg bg-green-500"><i data-lucide="shield" class="text-white"></i></div>
            </div>
            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <div>
                    <p class="text-sm font-medium text-gray-500">Weak Passwords</p>
                    <h3 class="text-3xl font-bold mt-2">${weak}</h3>
                </div>
                <div class="p-3 rounded-lg bg-orange-500"><i data-lucide="alert-triangle" class="text-white"></i></div>
            </div>
            <div class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <div>
                    <p class="text-sm font-medium text-gray-500">Favorites</p>
                    <h3 class="text-3xl font-bold mt-2">${favorites}</h3>
                </div>
                <div class="p-3 rounded-lg bg-purple-500"><i data-lucide="star" class="text-white"></i></div>
            </div>
        `;

        const recContainer = document.getElementById('recommendations-container');
        let recsHTML = '';

        if (weak > 0) {
            recsHTML += `
                <div class="flex items-start space-x-3 p-4 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                    <i data-lucide="alert-triangle" class="w-5 h-5 text-orange-600 mt-0.5"></i>
                    <div>
                        <h4 class="font-medium text-orange-900 dark:text-orange-100">Update Weak Passwords</h4>
                        <p class="text-sm text-orange-700 dark:text-orange-300 mt-1">You have ${weak} weak passwords.</p>
                    </div>
                </div>`;
        }
        if (reused > 0) {
            recsHTML += `
                <div class="flex items-start space-x-3 p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                    <i data-lucide="alert-triangle" class="w-5 h-5 text-red-600 mt-0.5"></i>
                    <div>
                        <h4 class="font-medium text-red-900 dark:text-red-100">Password Reuse Detected</h4>
                        <p class="text-sm text-red-700 dark:text-red-300 mt-1">You are reusing passwords.</p>
                    </div>
                </div>`;
        }
        if (total === 0) {
            recsHTML = '<div class="text-gray-500">No passwords yet. Go to Vault to add one!</div>';
        } else if (weak === 0 && reused === 0) {
            recsHTML = `
                <div class="flex items-start space-x-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
                    <i data-lucide="shield" class="w-5 h-5 text-green-600 mt-0.5"></i>
                    <div>
                        <h4 class="font-medium text-green-900 dark:text-green-100">Great Job!</h4>
                        <p class="text-sm text-green-700 dark:text-green-300 mt-1">Your vault is secure.</p>
                    </div>
                </div>`;
        }

        recContainer.innerHTML = recsHTML;
        lucide.createIcons();

    } catch (error) {
        console.error("Dashboard error", error);
    }
};
