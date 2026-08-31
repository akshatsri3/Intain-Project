import { useState, useEffect } from 'react';
import { verifiedService } from '../services/verifiedService';
import { auditService } from '../services/auditService';
import {
	formatCurrency,
	formatIndianNumber,
	formatIndianDate,
	formatIndianDateTime,
} from '../utils/formatters';
import {
	CheckCircle,
	Search,
	Download,
	FileText,
	Shield,
	Clock,
	X,
} from 'lucide-react';

export default function VerifiedLoans() {
	const [loans, setLoans] = useState([]);
	const [stats, setStats] = useState(null);
	const [loading, setLoading] = useState(true);
	const [searchQuery, setSearchQuery] = useState('');
	const [expandedId, setExpandedId] = useState(null);
	const [auditTrail, setAuditTrail] = useState([]);
	const [exporting, setExporting] = useState(false);

	useEffect(() => {
		const fetchData = async () => {
			setLoading(true);
			try {
				const [loanData, statsData] = await Promise.all([
					verifiedService.getLoans({
						search: searchQuery || undefined,
					}),
					verifiedService.getStats(),
				]);
				setLoans(loanData);
				setStats(statsData);
			} catch (e) {
				console.error(e);
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, [searchQuery]);

	const handleExport = async (format) => {
		setExporting(true);
		try {
			if (format === 'csv') await verifiedService.exportCsv();
			else await verifiedService.exportJson();
		} catch (e) {
			console.error(e);
		} finally {
			setExporting(false);
		}
	};

	const handleShowAudit = async (loanId) => {
		if (expandedId === loanId) {
			setExpandedId(null);
			return;
		}
		try {
			const trail = await auditService.getLoanTrail(loanId);
			setAuditTrail(trail);
			setExpandedId(loanId);
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
						<CheckCircle size={20} className="text-emerald-400" />
						Verified Loan Records
					</h2>
					<p className="mt-0.5 text-sm text-zinc-400">
						Browse, search, and export fully verified golden loan
						records.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<button
						id="export-csv-btn"
						onClick={() => handleExport('csv')}
						disabled={exporting || loans.length === 0}
						className="btn-secondary flex items-center gap-1.5 text-xs"
					>
						<Download size={13} /> Export CSV
					</button>
					<button
						id="export-json-btn"
						onClick={() => handleExport('json')}
						disabled={exporting || loans.length === 0}
						className="btn-primary flex items-center gap-1.5 text-xs"
					>
						<Download size={13} /> Export JSON
					</button>
				</div>
			</div>

			{/* Stats */}
			{stats && (
				<div className="grid grid-cols-2 gap-3 md:grid-cols-4">
					<div className="card flex items-center gap-4">
						<div className="flex h-10 w-10 items-center justify-center rounded-lg border border-emerald-800/50 bg-emerald-950/70">
							<CheckCircle
								size={18}
								className="text-emerald-400"
							/>
						</div>
						<div>
							<p className="text-xs text-zinc-400">Verified</p>
							<p className="font-mono text-xl font-bold text-white">
								{stats.verified}
							</p>
						</div>
					</div>
					<div className="card flex items-center gap-4">
						<div className="flex h-10 w-10 items-center justify-center rounded-lg border border-amber-800/50 bg-amber-950/70">
							<Clock size={18} className="text-amber-400" />
						</div>
						<div>
							<p className="text-xs text-zinc-400">Pending</p>
							<p className="font-mono text-xl font-bold text-white">
								{stats.pending}
							</p>
						</div>
					</div>
					<div className="card flex items-center gap-4">
						<div className="flex h-10 w-10 items-center justify-center rounded-lg border border-red-800/50 bg-red-950/70">
							<X size={18} className="text-red-400" />
						</div>
						<div>
							<p className="text-xs text-zinc-400">Rejected</p>
							<p className="font-mono text-xl font-bold text-white">
								{stats.rejected}
							</p>
						</div>
					</div>
					<div className="card flex items-center gap-4">
						<div className="flex h-10 w-10 items-center justify-center rounded-lg border border-zinc-700 bg-zinc-800">
							<Shield size={18} className="text-white" />
						</div>
						<div>
							<p className="text-xs text-zinc-400">
								Quality Score
							</p>
							<p className="font-mono text-xl font-bold text-white">
								{stats.quality_score}%
							</p>
						</div>
					</div>
				</div>
			)}

			{/* Search */}
			<div className="relative max-w-md">
				<Search
					size={15}
					className="absolute top-1/2 left-3 -translate-y-1/2 text-zinc-500"
				/>
				<input
					id="verified-search"
					type="text"
					placeholder="Search by Loan ID or Borrower ID..."
					value={searchQuery}
					onChange={(e) => setSearchQuery(e.target.value)}
					className="input-field pl-9"
				/>
			</div>

			{/* Loans Table */}
			{loading ? (
				<p className="py-6 text-sm text-zinc-500">
					Loading verified loans...
				</p>
			) : loans.length === 0 ? (
				<div className="card py-10 text-center">
					<FileText
						size={32}
						className="mx-auto mb-3 text-zinc-700"
					/>
					<p className="text-sm text-zinc-400">
						No verified loans found.
					</p>
				</div>
			) : (
				<div className="card overflow-hidden p-0">
					<div className="overflow-x-auto">
						<table className="w-full text-xs">
							<thead className="border-b border-zinc-800">
								<tr>
									{[
										'Loan ID',
										'Borrower',
										'Type',
										'Principal',
										'Balance',
										'Rate',
										'State',
										'Status',
										'Verified At',
										'SHA-256 Hash',
										'',
									].map((h) => (
										<th
											key={h}
											className="table-header px-4 py-3 text-left whitespace-nowrap"
										>
											{h}
										</th>
									))}
								</tr>
							</thead>
							<tbody className="divide-y divide-zinc-800/80">
								{loans.map((loan) => (
									<>
										<tr
											key={loan.id}
											className="transition-colors hover:bg-zinc-900/40"
										>
											<td className="px-4 py-2.5 font-mono font-medium text-zinc-200">
												{loan.loan_id || '—'}
											</td>
											<td className="px-4 py-2.5 font-mono text-zinc-400">
												{loan.borrower_id || '—'}
											</td>
											<td className="px-4 py-2.5 text-zinc-400">
												{loan.loan_type || '—'}
											</td>
											<td className="px-4 py-2.5 font-mono text-zinc-300">
												{formatCurrency(
													loan.original_principal,
												)}
											</td>
											<td className="px-4 py-2.5 font-mono text-zinc-300">
												{formatCurrency(
													loan.current_balance,
												)}
											</td>
											<td className="px-4 py-2.5 font-mono text-zinc-300">
												{loan.interest_rate != null
													? `${loan.interest_rate}%`
													: '—'}
											</td>
											<td className="px-4 py-2.5 text-zinc-400">
												{loan.borrower_state || '—'}
											</td>
											<td className="px-4 py-2.5">
												<span className="badge badge-green">
													{loan.verification_status}
												</span>
											</td>
											<td className="px-4 py-2.5 font-mono text-[11px] text-zinc-500">
												{formatIndianDate(
													loan.verified_at,
												)}
											</td>
											<td
												className="max-w-[100px] truncate px-4 py-2.5 font-mono text-[10px] text-zinc-500"
												title={loan.record_hash}
											>
												{loan.record_hash
													? loan.record_hash.slice(
															0,
															12,
														) + '…'
													: '—'}
											</td>
											<td className="px-4 py-2.5 text-right">
												<button
													onClick={() =>
														handleShowAudit(loan.id)
													}
													className="ml-auto flex items-center gap-1 text-xs font-medium text-zinc-300 hover:text-white"
												>
													<Clock size={12} /> Audit
												</button>
											</td>
										</tr>
										{expandedId === loan.id && (
											<tr key={`audit-${loan.id}`}>
												<td
													colSpan={11}
													className="bg-zinc-950 px-4 pb-4"
												>
													<div className="mt-1 rounded-lg border border-zinc-800 bg-zinc-900 p-4">
														<h4 className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-zinc-200">
															<Clock
																size={13}
																className="text-zinc-400"
															/>{' '}
															Audit Trail Timeline
															— Loan #{loan.id}
														</h4>
														{auditTrail.length ===
														0 ? (
															<p className="text-xs text-zinc-500">
																No audit events
																recorded for
																this loan.
															</p>
														) : (
															<div className="space-y-2">
																{auditTrail.map(
																	(evt) => (
																		<div
																			key={
																				evt.id
																			}
																			className="flex items-start gap-3 text-xs"
																		>
																			<div className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-white" />
																			<div className="flex-1">
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
																				{evt.details_json && (
																					<p className="mt-0.5 font-mono text-[11px] text-zinc-400">
																						{JSON.stringify(
																							evt.details_json,
																						).slice(
																							0,
																							120,
																						)}
																					</p>
																				)}
																			</div>
																		</div>
																	),
																)}
															</div>
														)}
													</div>
												</td>
											</tr>
										)}
									</>
								))}
							</tbody>
						</table>
					</div>
				</div>
			)}
		</div>
	);
}
