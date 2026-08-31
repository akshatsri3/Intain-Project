/**
 * Formatting utilities for Indian Locale (en-IN).
 */

export function formatCurrency(amount) {
	if (amount == null || amount === '') return '—';
	const num = Number(amount);
	if (isNaN(num)) return String(amount);
	return `₹${num.toLocaleString('en-IN', {
		minimumFractionDigits: 0,
		maximumFractionDigits: 2,
	})}`;
}

export function formatIndianNumber(num) {
	if (num == null || num === '') return '0';
	const val = Number(num);
	if (isNaN(val)) return String(num);
	return val.toLocaleString('en-IN');
}

export function formatIndianDate(dateStr) {
	if (!dateStr) return '—';
	const d = new Date(dateStr);
	if (isNaN(d.getTime())) return String(dateStr);
	return d.toLocaleDateString('en-IN');
}

export function formatIndianDateTime(dateStr) {
	if (!dateStr) return '—';
	const d = new Date(dateStr);
	if (isNaN(d.getTime())) return String(dateStr);
	return d.toLocaleString('en-IN');
}
