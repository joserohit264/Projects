import { api } from './api.js';
import { generatePassword, showToast } from './utils.js';

let passwords = [];

export const initVault = async () => {
    const grid = document.getElementById('passwords-grid');
    const addBtn = document.getElementById('add-password-btn');
    const modal = document.getElementById('password-modal');
    const closeModal = document.getElementById('close-modal');
    const form = document.getElementById('password-form');
    const generateBtn = document.getElementById('generate-btn');

    const renderPasswords = () => {
        if (passwords.length === 0) {
            grid.innerHTML = '<div class="col-span-full text-center py-10 text-gray-500">No passwords found.</div>';
            return;
        }

        grid.innerHTML = passwords.map(p => `
            <div class="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow group">
                <div class="flex items-start justify-between mb-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center text-blue-600">
                            <i data-lucide="globe" class="w-5 h-5"></i>
                        </div>
                        <div>
                            <h3 class="font-bold text-lg">${p.website}</h3>
                            <p class="text-sm text-gray-500">${p.username}</p>
                        </div>
                    </div>
                    <div class="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button onclick="window.editPassword(${p.id})" class="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                            <i data-lucide="edit" class="w-4 h-4"></i>
                        </button>
                        <button onclick="window.deletePassword(${p.id})" class="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg">
                            <i data-lucide="trash-2" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
                <div class="bg-gray-50 dark:bg-gray-900 rounded-lg p-3 flex items-center justify-between">
                    <div class="font-mono text-sm truncate mr-2 password-text" data-password="${p.password}">••••••••••••</div>
                    <div class="flex items-center space-x-1">
                        <button onclick="window.togglePassword(this)" class="p-1.5 text-gray-400 hover:text-gray-600 rounded">
                            <i data-lucide="eye" class="w-4 h-4"></i>
                        </button>
                        <button onclick="window.copyPassword('${p.password}')" class="p-1.5 text-gray-400 hover:text-gray-600 rounded">
                            <i data-lucide="copy" class="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
        lucide.createIcons();
    };

    const fetchPasswords = async () => {
        try {
            passwords = await api.get('/passwords');
            renderPasswords();
        } catch (error) {
            console.error(error);
        }
    };

    // Global handlers for inline onclicks
    window.editPassword = (id) => {
        const p = passwords.find(x => x.id === id);
        if (!p) return;
        form.id.value = p.id;
        form.website.value = p.website;
        form.username.value = p.username;
        form.password.value = p.password;
        document.getElementById('modal-title').innerText = 'Edit Password';
        modal.classList.remove('hidden');
    };

    window.deletePassword = async (id) => {
        if (!confirm('Are you sure?')) return;
        try {
            await api.delete(`/passwords/${id}`);
            showToast('Password deleted');
            fetchPasswords();
        } catch (error) {
            showToast('Failed to delete', 'error');
        }
    };

    window.togglePassword = (btn) => {
        const container = btn.closest('.bg-gray-50');
        const textDiv = container.querySelector('.password-text');
        const isHidden = textDiv.innerText === '••••••••••••';

        if (isHidden) {
            textDiv.innerText = textDiv.dataset.password;
            btn.innerHTML = '<i data-lucide="eye-off" class="w-4 h-4"></i>';
        } else {
            textDiv.innerText = '••••••••••••';
            btn.innerHTML = '<i data-lucide="eye" class="w-4 h-4"></i>';
        }
        lucide.createIcons();
    };

    window.copyPassword = (text) => {
        navigator.clipboard.writeText(text);
        showToast('Password copied');
    };

    addBtn.onclick = () => {
        form.reset();
        form.id.value = '';
        document.getElementById('modal-title').innerText = 'Add Password';
        modal.classList.remove('hidden');
    };

    closeModal.onclick = () => {
        modal.classList.add('hidden');
    };

    generateBtn.onclick = () => {
        form.password.value = generatePassword();
    };

    form.onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            website: form.website.value,
            username: form.username.value,
            password: form.password.value
        };
        const id = form.id.value;

        try {
            if (id) {
                await api.put(`/passwords/${id}`, data);
                showToast('Password updated');
            } else {
                await api.post('/passwords', data);
                showToast('Password added');
            }
            modal.classList.add('hidden');
            fetchPasswords();
        } catch (error) {
            showToast('Failed to save', 'error');
        }
    };

    await fetchPasswords();
};
