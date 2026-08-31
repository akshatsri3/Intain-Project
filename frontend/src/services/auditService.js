import api from './api';

export const auditService = {
	getTrail: async (entityType, entityId) => {
		const response = await api.get(
			`/audit/trail/${entityType}/${entityId}`,
		);
		return response.data;
	},

	getRecent: async ({
		entityType,
		eventType,
		limit = 50,
		offset = 0,
	} = {}) => {
		const params = { limit, offset };
		if (entityType) params.entity_type = entityType;
		if (eventType) params.event_type = eventType;
		const response = await api.get('/audit/recent', { params });
		return response.data;
	},

	getLoanTrail: async (loanId) => {
		const response = await api.get(`/audit/loan/${loanId}`);
		return response.data;
	},
};
