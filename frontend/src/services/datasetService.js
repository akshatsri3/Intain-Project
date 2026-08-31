import api from './api';

export const datasetService = {
	upload: async (file, sourceType) => {
		const formData = new FormData();
		formData.append('file', file);
		formData.append('source_type', sourceType);
		const response = await api.post('/datasets/upload', formData, {
			headers: { 'Content-Type': 'multipart/form-data' },
		});
		return response.data; // ImportSummaryResponse
	},

	list: async () => {
		const response = await api.get('/datasets');
		return response.data; // DatasetResponse[]
	},

	getById: async (id) => {
		const response = await api.get(`/datasets/${id}`);
		return response.data; // DatasetResponse
	},

	getSummary: async (id) => {
		const response = await api.get(`/datasets/${id}/summary`);
		return response.data; // ImportSummaryResponse
	},

	getErrors: async (id) => {
		const response = await api.get(`/datasets/${id}/errors`);
		return response.data; // ImportErrorResponse[]
	},

	getRecords: async (id, limit = 50, offset = 0) => {
		const response = await api.get(`/datasets/${id}/records`, {
			params: { limit, offset },
		});
		return response.data; // LoanResponse[]
	},
};
