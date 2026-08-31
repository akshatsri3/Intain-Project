import api from './api';

export const authService = {
	login: async (email, password) => {
		const response = await api.post('/auth/login', { email, password });
		return response.data; // { access_token, token_type, user }
	},

	register: async (name, email, password, role) => {
		const response = await api.post('/auth/register', { name, email, password, role });
		return response.data; // UserResponse { id, name, email, role }
	},

	getMe: async () => {
		const response = await api.get('/auth/me');
		return response.data; // { id, name, email, role }
	},
};
