import api from './api';

export const verifiedService = {
	getLoans: async ({
		search,
		loanType,
		borrowerState,
		limit = 50,
		offset = 0,
	} = {}) => {
		const params = { limit, offset };
		if (search) params.search = search;
		if (loanType) params.loan_type = loanType;
		if (borrowerState) params.borrower_state = borrowerState;
		const response = await api.get('/verified/loans', { params });
		return response.data;
	},

	getLoan: async (id) => {
		const response = await api.get(`/verified/loans/${id}`);
		return response.data;
	},

	getStats: async () => {
		const response = await api.get('/verified/stats');
		return response.data;
	},

	exportCsv: async () => {
		const response = await api.get('/verified/export?format=csv', {
			responseType: 'blob',
		});
		const url = window.URL.createObjectURL(new Blob([response.data]));
		const a = document.createElement('a');
		a.href = url;
		a.download = 'verified_loans.csv';
		a.click();
		window.URL.revokeObjectURL(url);
	},

	exportJson: async () => {
		const response = await api.get('/verified/export?format=json', {
			responseType: 'blob',
		});
		const url = window.URL.createObjectURL(new Blob([response.data]));
		const a = document.createElement('a');
		a.href = url;
		a.download = 'verified_loans.json';
		a.click();
		window.URL.revokeObjectURL(url);
	},
};
