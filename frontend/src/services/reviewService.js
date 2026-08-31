import api from './api';

export const reviewService = {
	submitDecision: async (
		exceptionId,
		{ decision, override_value, reviewer_note, ai_suggestion_json },
	) => {
		const response = await api.post(`/reviews/decide/${exceptionId}`, {
			decision,
			override_value,
			reviewer_note,
			ai_suggestion_json,
		});
		return response.data;
	},

	getPending: async (limit = 50, offset = 0) => {
		const response = await api.get('/reviews/pending', {
			params: { limit, offset },
		});
		return response.data;
	},

	getDecisions: async (limit = 50, offset = 0) => {
		const response = await api.get('/reviews/decisions', {
			params: { limit, offset },
		});
		return response.data;
	},
};
