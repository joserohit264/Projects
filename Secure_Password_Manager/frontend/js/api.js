const API_BASE = '/api';

export const api = {
    async request(endpoint, method = 'GET', body = null) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json',
        };
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers,
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_BASE}${endpoint}`, config);

            if (response.status === 401) {
                // Unauthorized, clear token and redirect
                localStorage.removeItem('access_token');
                localStorage.removeItem('user');
                window.location.hash = '#login';
                throw new Error('Unauthorized');
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'API Request Failed');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    get(endpoint) {
        return this.request(endpoint, 'GET');
    },

    post(endpoint, body) {
        return this.request(endpoint, 'POST', body);
    },

    put(endpoint, body) {
        return this.request(endpoint, 'PUT', body);
    },

    delete(endpoint) {
        return this.request(endpoint, 'DELETE');
    }
};
