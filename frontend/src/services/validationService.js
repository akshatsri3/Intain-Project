import api from './api';

export const validationService = {
	runValidation: async (datasetId) => {
		const response = await api.post(`/validation/run/${datasetId}`);
		return response.data;
	},

	getExceptions: async ({
		status,
		severity,
		ruleCode,
		search,
		datasetId,
		limit = 50,
		offset = 0,
	} = {}) => {
		const params = { limit, offset };
		if (status) params.status = status;
		if (severity) params.severity = severity;
		if (ruleCode) params.rule_code = ruleCode;
		if (search) params.search = search;
		if (datasetId) params.dataset_id = datasetId;
		const response = await api.get('/validation/exceptions', { params });
		return response.data;
	},

	getException: async (id) => {
		const response = await api.get(`/validation/exceptions/${id}`);
		return response.data;
	},

	getStats: async (datasetId) => {
		const params = datasetId ? { dataset_id: datasetId } : {};
		const response = await api.get('/validation/stats', { params });
		return response.data;
	},

	resolveException: async (id, { status, resolution_note }) => {
		const response = await api.patch(`/validation/exceptions/${id}`, {
			status,
			resolution_note,
		});
		return response.data;
	},

	getBatchSummary: async (datasetId) => {
		const params = datasetId ? { dataset_id: datasetId } : {};
		const response = await api.get('/validation/batch-summary', { params });
		return response.data;
	},
};
