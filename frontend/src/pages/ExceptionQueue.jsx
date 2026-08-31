import { useState, useEffect, useCallback } from 'react';
import { validationService } from '../services/validationService';
import { reviewService } from '../services/reviewService';
import { auditService } from '../services/auditService';
import { useAuth } from '../context/AuthContext';
import { formatIndianNumber, formatIndianDateTime } from '../utils/formatters';
import {
	AlertTriangle,
	Search,
	Brain,
	CheckCircle,
	XCircle,
	Flag,
	Edit3,
	ChevronDown,
	ChevronUp,
	Sparkles,
	X,
	Clock,
	Shield,
	ArrowRight,
} from 'lucide-react';

const SEVERITY_BADGE = {
	ERROR: 'bg-red-950/70 border border-red-800/50 text-red-300',
	WARNING: 'bg-amber-950/70 border border-amber-800/50 text-amber-300',
	INFO: 'bg-blue-950/70 border border-blue-800/50 text-blue-300',
};

const STATUS_BADGE = {
	OPEN: 'bg-zinc-900 border border-zinc-700 text-zinc-300',
	RESOLVED: 'bg-emerald-950/70 border border-emerald-800/50 text-emerald-300',
	DISMISSED: 'bg-zinc-800 border border-zinc-700 text-zinc-400',
};

const CONFIDENCE_COLOR = {
	HIGH: 'text-emerald-400 font-semibold',
	MEDIUM: 'text-amber-400 font-semibold',
	LOW: 'text-zinc-400 font-semibold',
};

function StatCard({ icon: Icon, label, value, color }) {
	return (
		<div className="card flex items-center gap-4">
			<div
				className={`flex h-10 w-10 items-center justify-center rounded-lg ${color}`}
			>
				<Icon size={18} className="text-white" />
			</div>
			<div>
				<p className="text-xs text-zinc-400">{label}</p>
				<p className="font-mono text-xl font-bold text-white">
					{value}
				</p>
			</div>
		</div>
	);
}

export default function ExceptionQueue() {
	const { user } = useAuth();
	const isReviewer = user?.role === 'REVIEWER';

	const [exceptions, setExceptions] = useState([]);
	const [stats, setStats] = useState(null);
	const [batchSummary, setBatchSummary] = useState(null);
	const [loading, setLoading] = useState(true);
	const [expandedId, setExpandedId] = useState(null);

	// Filters
	const [statusFilter, setStatusFilter] = useState('OPEN');
	const [severityFilter, setSeverityFilter] = useState('');
	const [searchQuery, setSearchQuery] = useState('');

	// Review modal
	const [reviewingExc, setReviewingExc] = useState(null);
	const [decisionType, setDecisionType] = useState('');
	const [overrideValue, setOverrideValue] = useState('');
	const [reviewerNote, setReviewerNote] = useState('');
	const [submitting, setSubmitting] = useState(false);

	// Audit trail
	const [auditTrail, setAuditTrail] = useState([]);
	const [showAudit, setShowAudit] = useState(null);

	const fetchData = useCallback(async () => {
		setLoading(true);
		try {
			const [excs, st] = await Promise.all([
				validationService.getExceptions({
					status: statusFilter || undefined,
					severity: severityFilter || undefined,
					search: searchQuery || undefined,
				}),
				validationService.getStats(),
			]);
			setExceptions(excs);
			setStats(st);
		} catch (e) {
			console.error(e);
		} finally {
			setLoading(false);
		}
	}, [statusFilter, severityFilter, searchQuery]);

	useEffect(() => {
		fetchData();
	}, [fetchData]);

	const handleLoadBatchSummary = async () => {
		try {
			const summary = await validationService.getBatchSummary();
			setBatchSummary(summary);
		} catch (e) {
			console.error(e);
		}
	};

	const handleSubmitDecision = async () => {
		if (!reviewingExc || !decisionType) return;
		setSubmitting(true);
		try {
			await reviewService.submitDecision(reviewingExc.id, {
				decision: decisionType,
				override_value: overrideValue || null,
				reviewer_note: reviewerNote || null,
				ai_suggestion_json: reviewingExc.ai_suggestion || null,
			});
			setReviewingExc(null);
			setDecisionType('');
			setOverrideValue('');
			setReviewerNote('');
			fetchData();
		} catch (e) {
			console.error(e);
		} finally {
			setSubmitting(false);
		}
	};

	const handleShowAudit = async (loanId) => {
		try {
			const trail = await auditService.getLoanTrail(loanId);
			setAuditTrail(trail);
			setShowAudit(loanId);
		} catch (e) {
			console.error(e);
		}
	};

	return (
		<div className="space-y-5">
			{/* Header */}
			<div className="flex items-center justify-between">
				<div>
					<h2 className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
						<AlertTriangle size={20} className="text-amber-400" />
						Exception Queue
					</h2>
					<p className="mt-0.5 text-sm text-zinc-400">
						Review and resolve validation exceptions with
						AI-assisted recommendations.
					</p>
				</div>
				<button
					onClick={handleLoadBatchSummary}
					className="btn-secondary flex items-center gap-2 text-xs"
				>
					<Sparkles size={14} className="text-purple-400" /> AI Batch
					Summary
				</button>
			</div>

			{/* Stats */}
			{stats && (
				<div className="grid grid-cols-2 gap-3 md:grid-cols-4">
					<StatCard
						icon={AlertTriangle}
						label="Open"
						value={formatIndianNumber(stats.open)}
						color="bg-amber-950/70 border border-amber-800/50"
					/>
					<StatCard
						icon={CheckCircle}
						label="Resolved"
						value={formatIndianNumber(stats.resolved)}
						color="bg-emerald-950/70 border border-emerald-800/50"
					/>
					<StatCard
						icon={XCircle}
						label="Errors"
						value={formatIndianNumber(stats.errors)}
						color="bg-red-950/70 border border-red-800/50"
					/>
					<StatCard
						icon={Shield}
						label="Total Exceptions"
						value={formatIndianNumber(stats.total)}
						color="bg-zinc-800 border border-zinc-700"
					/>
				</div>
			)}

			{/* Batch Summary Card */}
			{batchSummary && (
				<div className="card border-zinc-700 bg-zinc-950">
					<div className="mb-3 flex items-center justify-between">
						<h3 className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
							<Brain size={16} className="text-purple-400" /> AI
							Portfolio Analysis
						</h3>
						<div className="flex items-center gap-2">
							<span className="font-mono text-xs text-zinc-500">
								Model: {batchSummary.model}
							</span>
							<button
								onClick={() => setBatchSummary(null)}
								className="text-zinc-500 hover:text-zinc-300"
							>
								<X size={14} />
							</button>
						</div>
					</div>
					<p className="mb-3 text-sm leading-relaxed text-zinc-300">
						{batchSummary.summary}
					</p>
					{batchSummary.recommendations?.length > 0 && (
						<div className="space-y-1.5 border-t border-zinc-800 pt-2">
							<p className="text-xs font-semibold tracking-wider text-zinc-400 uppercase">
								Recommendations
							</p>
							{batchSummary.recommendations.map((rec, i) => (
								<div
									key={i}
									className="flex items-start gap-2 text-xs text-zinc-300"
								>
									<ArrowRight
										size={12}
										className="mt-0.5 shrink-0 text-white"
									/>
									<span>{rec}</span>
								</div>
							))}
						</div>
					)}
				</div>
			)}

			{/* Filters */}
			<div className="flex flex-wrap items-center gap-3">
				<div className="relative max-w-sm min-w-[200px] flex-1">
					<Search
						size={15}
						className="absolute top-1/2 left-3 -translate-y-1/2 text-zinc-500"
					/>
					<input
						id="exception-search"
						type="text"
						placeholder="Search by Loan ID or Borrower ID..."
						value={searchQuery}
						onChange={(e) => setSearchQuery(e.target.value)}
						className="input-field pl-9"
					/>
				</div>
				<select
					id="filter-status"
					value={statusFilter}
					onChange={(e) => setStatusFilter(e.target.value)}
					className="input-field w-auto min-w-[130px]"
				>
					<option value="" className="bg-zinc-900 text-zinc-100">
						All Statuses
					</option>
					<option value="OPEN" className="bg-zinc-900 text-zinc-100">
						Open
					</option>
					<option
						value="RESOLVED"
						className="bg-zinc-900 text-zinc-100"
					>
						Resolved
					</option>
					<option
						value="DISMISSED"
						className="bg-zinc-900 text-zinc-100"
					>
						Dismissed
					</option>
				</select>
				<select
					id="filter-severity"
					value={severityFilter}
					onChange={(e) => setSeverityFilter(e.target.value)}
					className="input-field w-auto min-w-[130px]"
				>
					<option value="" className="bg-zinc-900 text-zinc-100">
						All Severities
					</option>
					<option value="ERROR" className="bg-zinc-900 text-zinc-100">
						Error
					</option>
					<option
						value="WARNING"
						className="bg-zinc-900 text-zinc-100"
					>
						Warning
					</option>
					<option value="INFO" className="bg-zinc-900 text-zinc-100">
						Info
					</option>
				</select>
			</div>

			{/* Exception List */}
			{loading ? (
				<p className="py-6 text-sm text-zinc-500">
					Loading exceptions...
				</p>
			) : exceptions.length === 0 ? (
				<div className="card py-10 text-center">
					<CheckCircle
						size={32}
						className="mx-auto mb-3 text-emerald-500"
					/>
					<p className="text-sm text-zinc-400">
						No exceptions found matching your filters.
					</p>
				</div>
			) : (
				<div className="space-y-2">
					{exceptions.map((exc) => {
						const isExpanded = expandedId === exc.id;
						return (
							<div
								key={exc.id}
								className="card overflow-hidden p-0"
							>
								{/* Exception Row Header */}
								<button
									onClick={() =>
										setExpandedId(
											isExpanded ? null : exc.id,
										)
									}
									className="flex w-full items-center gap-3 px-5 py-3.5 text-left transition-colors hover:bg-zinc-900/50"
								>
									<span
										className={`badge text-xs ${SEVERITY_BADGE[exc.severity]}`}
									>
										{exc.severity}
									</span>
									<span
										className={`badge text-xs ${STATUS_BADGE[exc.status]}`}
									>
										{exc.status}
									</span>
									<span className="flex-1 truncate text-sm font-medium text-zinc-200">
										{exc.rule_code.replace(/_/g, ' ')}
									</span>
									<span className="font-mono text-xs text-zinc-400">
										{exc.loan_loan_id ||
											`Loan #${exc.loan_id}`}
									</span>
									{isExpanded ? (
										<ChevronUp
											size={16}
											className="text-zinc-500"
										/>
									) : (
										<ChevronDown
											size={16}
											className="text-zinc-500"
										/>
									)}
								</button>

								{/* Expanded Detail */}
								{isExpanded && (
									<div className="border-t border-zinc-800/80 px-5 pb-5">
										<div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
											{/* Exception Details */}
											<div className="space-y-3">
												<h4 className="text-xs font-semibold tracking-wider text-zinc-400 uppercase">
													Exception Detail
												</h4>
												<p className="text-sm font-medium text-red-400">
													{exc.message}
												</p>
												<div className="grid grid-cols-2 gap-2 text-xs">
													<div>
														<span className="text-zinc-500">
															Field:
														</span>
														<span className="ml-1 font-mono text-zinc-300">
															{exc.field_name ||
																'—'}
														</span>
													</div>
													<div>
														<span className="text-zinc-500">
															Current Value:
														</span>
														<span className="ml-1 font-mono text-zinc-300">
															{exc.current_value ||
																'—'}
														</span>
													</div>
													<div>
														<span className="text-zinc-500">
															Expected:
														</span>
														<span className="ml-1 text-zinc-300">
															{exc.expected_range ||
																'—'}
														</span>
													</div>
													<div>
														<span className="text-zinc-500">
															Loan ID:
														</span>
														<span className="ml-1 font-mono text-zinc-300">
															{exc.loan_loan_id ||
																'—'}
														</span>
													</div>
													<div>
														<span className="text-zinc-500">
															Borrower ID:
														</span>
														<span className="ml-1 font-mono text-zinc-300">
															{exc.loan_borrower_id ||
																'—'}
														</span>
													</div>
												</div>

												{/* Audit Trail Button */}
												<button
													onClick={() =>
														handleShowAudit(
															exc.loan_id,
														)
													}
													className="flex items-center gap-1 pt-1 text-xs text-zinc-300 hover:text-white"
												>
													<Clock size={12} /> View
													Loan Audit Trail
												</button>

												{/* Inline Audit Trail */}
												{showAudit === exc.loan_id &&
													auditTrail.length > 0 && (
														<div className="mt-2 max-h-40 space-y-2 overflow-y-auto rounded-lg border border-zinc-800 bg-zinc-900 p-3">
															{auditTrail.map(
																(evt) => (
																	<div
																		key={
																			evt.id
																		}
																		className="flex items-start gap-2 text-xs"
																	>
																		<div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-white" />
																		<div>
																			<span className="font-medium text-zinc-200">
																				{
																					evt.event_type
																				}
																			</span>
																			<span className="ml-2 font-mono text-[11px] text-zinc-500">
																				{formatIndianDateTime(
																					evt.created_at,
																				)}
																			</span>
																		</div>
																	</div>
																),
															)}
														</div>
													)}
											</div>

											{/* AI Suggestion Panel */}
											{exc.ai_suggestion && (
												<div className="space-y-3 rounded-lg border border-zinc-700/80 bg-zinc-900 p-4">
													<div className="flex items-center justify-between">
														<h4 className="flex items-center gap-1.5 text-xs font-semibold tracking-wider text-zinc-200 uppercase">
															<Brain
																size={14}
																className="text-purple-400"
															/>{' '}
															AI Recommendation
														</h4>
														<span
															className={`text-xs ${CONFIDENCE_COLOR[exc.ai_suggestion.confidence]}`}
														>
															Confidence:{' '}
															{
																exc
																	.ai_suggestion
																	.confidence
															}
														</span>
													</div>
													<p className="text-sm font-medium text-white">
														{
															exc.ai_suggestion
																.suggested_action
														}
													</p>
													<p className="text-xs leading-relaxed text-zinc-400">
														{
															exc.ai_suggestion
																.explanation
														}
													</p>
													<div className="text-right">
														<span className="font-mono text-[11px] text-zinc-500">
															Model:{' '}
															{
																exc
																	.ai_suggestion
																	.model
															}
														</span>
													</div>
												</div>
											)}
										</div>

										{/* Action Buttons (Reviewer only) */}
										{isReviewer &&
											exc.status === 'OPEN' && (
												<div className="mt-4 flex flex-wrap gap-2 border-t border-zinc-800 pt-3">
													<button
														onClick={() => {
															setReviewingExc(
																exc,
															);
															setDecisionType(
																'ACCEPT_SUGGESTION',
															);
														}}
														className="flex items-center gap-1.5 rounded-lg border border-emerald-800/50 bg-emerald-950/70 px-3 py-1.5 text-xs font-medium text-emerald-300 transition-colors hover:bg-emerald-900/60"
													>
														<CheckCircle
															size={13}
														/>{' '}
														Accept Suggestion
													</button>
													<button
														onClick={() => {
															setReviewingExc(
																exc,
															);
															setDecisionType(
																'MANUAL_OVERRIDE',
															);
														}}
														className="flex items-center gap-1.5 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-1.5 text-xs font-medium text-zinc-200 transition-colors hover:bg-zinc-800"
													>
														<Edit3 size={13} />{' '}
														Manual Override
													</button>
													<button
														onClick={() => {
															setReviewingExc(
																exc,
															);
															setDecisionType(
																'REJECT_LOAN',
															);
														}}
														className="flex items-center gap-1.5 rounded-lg border border-red-800/50 bg-red-950/70 px-3 py-1.5 text-xs font-medium text-red-300 transition-colors hover:bg-red-900/60"
													>
														<XCircle size={13} />{' '}
														Reject Loan
													</button>
													<button
														onClick={() => {
															setReviewingExc(
																exc,
															);
															setDecisionType(
																'FLAG_FOR_AUDIT',
															);
														}}
														className="flex items-center gap-1.5 rounded-lg border border-amber-800/50 bg-amber-950/70 px-3 py-1.5 text-xs font-medium text-amber-300 transition-colors hover:bg-amber-900/60"
													>
														<Flag size={13} /> Flag
														for Audit
													</button>
												</div>
											)}
									</div>
								)}
							</div>
						);
					})}
				</div>
			)}

			{/* Review Decision Modal */}
			{reviewingExc && (
				<div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
					<div className="w-full max-w-lg space-y-4 rounded-xl border border-zinc-700 bg-zinc-950 p-6 shadow-2xl">
						<div className="flex items-center justify-between border-b border-zinc-800 pb-3">
							<h3 className="text-sm font-semibold text-white">
								Submit Review Decision
							</h3>
							<button
								onClick={() => setReviewingExc(null)}
								className="text-zinc-500 hover:text-zinc-300"
							>
								<X size={18} />
							</button>
						</div>

						<div className="space-y-1.5 rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-xs">
							<p className="text-zinc-400">
								Exception:{' '}
								<span className="font-medium text-zinc-200">
									{reviewingExc.rule_code.replace(/_/g, ' ')}
								</span>
							</p>
							<p className="text-zinc-400">
								Loan ID:{' '}
								<span className="font-mono text-zinc-200">
									{reviewingExc.loan_loan_id ||
										`#${reviewingExc.loan_id}`}
								</span>
							</p>
							<p className="text-zinc-400">
								Selected Action:{' '}
								<span className="font-bold text-white">
									{decisionType.replace(/_/g, ' ')}
								</span>
							</p>
						</div>

						{decisionType === 'MANUAL_OVERRIDE' && (
							<div>
								<label className="mb-1 block text-xs font-medium text-zinc-300">
									Corrected Field Value
								</label>
								<input
									id="override-value-input"
									type="text"
									value={overrideValue}
									onChange={(e) =>
										setOverrideValue(e.target.value)
									}
									placeholder={`Current value: ${reviewingExc.current_value || '—'}`}
									className="input-field font-mono"
								/>
							</div>
						)}

						<div>
							<label className="mb-1 block text-xs font-medium text-zinc-300">
								Reviewer Note / Justification
							</label>
							<textarea
								id="reviewer-note-input"
								value={reviewerNote}
								onChange={(e) =>
									setReviewerNote(e.target.value)
								}
								placeholder="Add a comment explaining the rationale for this decision..."
								className="input-field min-h-[80px] resize-none"
								rows={3}
							/>
						</div>

						<div className="flex justify-end gap-2 border-t border-zinc-800 pt-2">
							<button
								onClick={() => setReviewingExc(null)}
								className="btn-secondary text-xs"
							>
								Cancel
							</button>
							<button
								id="submit-decision-btn"
								onClick={handleSubmitDecision}
								disabled={submitting}
								className="btn-primary text-xs"
							>
								{submitting
									? 'Submitting...'
									: 'Confirm Decision'}
							</button>
						</div>
					</div>
				</div>
			)}
		</div>
	);
}
