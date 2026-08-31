import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { verifiedService } from '../services/verifiedService';
import {
	formatCurrency,
	formatIndianNumber,
	formatIndianDate,
} from '../utils/formatters';
import {
	CheckCircle,
	Shield,
	Download,
	ArrowRight,
	FileText,
	Clock,
	X,
} from 'lucide-react';

function StatCard({ icon: Icon, label, value, color, onClick }) {
	return (
		<button
			onClick={onClick}
			className={`card flex w-full items-center gap-4 text-left transition-colors ${
				onClick ? 'cursor-pointer hover:border-zinc-700' : ''
			}`}
		>
			<div
				className={`flex h-10 w-10 items-center justify-center rounded-lg ${color}`}
			>
				<Icon size={18} className="text-white" />
			</div>
			<div>
				<p className="text-xs text-zinc-400">{label}</p>
				<p className="font-mono text-2xl font-bold text-white">
					{value}
				</p>
			</div>
		</button>
	);
}

export default function ConsumerDashboard() {
	const { user } = useAuth();
	const navigate = useNavigate();
	const [stats, setStats] = useState(null);
	const [recentVerified, setRecentVerified] = useState([]);
	const [loading, setLoading] = useState(true);
	const [exporting, setExporting] = useState(false);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const [st, loans] = await Promise.all([
					verifiedService.getStats(),
					verifiedService.getLoans({ limit: 5 }),
				]);
				setStats(st);
				setRecentVerified(loans);
			} catch (e) {
				console.error(e);
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, []);

	const handleExport = async (format) => {
		setExporting(true);
		try {
			if (format === 'csv') {
				await verifiedService.exportCsv();
			} else {
				await verifiedService.exportJson();
			}
		} catch (e) {
			console.error(e);
		} finally {
			setExporting(false);
		}
	};

	return (
		<div className="space-y-6">
			{/* Welcome & Actions */}
			<div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
				<div>
					<h2 className="text-xl font-bold tracking-tight text-white">
						Welcome, {user?.name?.split(' ')[0]}
					</h2>
					<p className="mt-0.5 text-sm text-zinc-400">
						Access trusted golden records, monitor data quality, and
						export verified portfolios.
					</p>
				</div>
				<div className="flex items-center gap-2">
					<button
						id="consumer-export-csv-btn"
						onClick={() => handleExport('csv')}
						disabled={exporting || stats?.verified === 0}
						className="btn-secondary flex items-center gap-1.5 text-xs"
					>
						<Download size={13} /> Export CSV
					</button>
					<button
						id="consumer-export-json-btn"
						onClick={() => handleExport('json')}
						disabled={exporting || stats?.verified === 0}
						className="btn-primary flex items-center gap-1.5 text-xs"
					>
						<Download size={13} /> Export JSON
					</button>
				</div>
			</div>

			{/* Portfolio Stats */}
			{stats && (
				<div className="grid grid-cols-2 gap-3 md:grid-cols-4">
					<StatCard
						icon={Shield}
						label="Quality Score"
						value={`${stats.quality_score}%`}
						color="bg-zinc-800 border border-zinc-700"
					/>
					<StatCard
						icon={CheckCircle}
						label="Verified Loans"
						value={formatIndianNumber(stats.verified)}
						color="bg-emerald-950/70 border border-emerald-800/50"
						onClick={() => navigate('/verified')}
					/>
					<StatCard
						icon={Clock}
						label="Pending Verification"
						value={formatIndianNumber(stats.pending)}
						color="bg-amber-950/70 border border-amber-800/50"
					/>
					<StatCard
						icon={X}
						label="Rejected"
						value={formatIndianNumber(stats.rejected)}
						color="bg-red-950/70 border border-red-800/50"
					/>
				</div>
			)}

			{/* Quality Score Banner */}
			<div className="card border-zinc-800 bg-zinc-950">
				<div className="flex flex-col items-start justify-between gap-4 md:flex-row md:items-center">
					<div className="space-y-1">
						<div className="flex items-center gap-2">
							<Shield size={18} className="text-white" />
							<h3 className="text-sm font-semibold text-white">
								Portfolio Verification Health
							</h3>
						</div>
						<p className="max-w-xl text-xs leading-relaxed text-zinc-400">
							{stats?.quality_score >= 80
								? 'High data integrity: The majority of ingested records meet schema rules and verification checks.'
								: stats?.quality_score >= 50
									? 'Moderate data integrity: Pending reviewer exceptions are under evaluation.'
									: 'Attention needed: A significant number of records require reviewer resolution before verification.'}
						</p>
					</div>
					<div className="flex items-center gap-3">
						<div className="text-right">
							<span className="font-mono text-2xl font-bold text-white">
								{formatIndianNumber(stats?.verified || 0)}
							</span>
							<span className="font-mono text-xs text-zinc-500">
								{' '}
								/ {formatIndianNumber(
									stats?.total_loans || 0,
								)}{' '}
								Total
							</span>
						</div>
					</div>
				</div>
			</div>

			{/* Recent Verified Records */}
			<div className="card overflow-hidden p-0">
				<div className="flex items-center justify-between border-b border-zinc-800/80 px-5 py-4">
					<div className="flex items-center gap-2">
						<CheckCircle size={16} className="text-emerald-400" />
						<h3 className="section-title">
							Recently Verified Loans
						</h3>
					</div>
					<button
						onClick={() => navigate('/verified')}
						className="flex items-center gap-1 text-xs text-zinc-400 hover:text-white"
					>
						View All Verified <ArrowRight size={13} />
					</button>
				</div>

				{loading ? (
					<p className="p-5 text-sm text-zinc-500">
						Loading verified records...
					</p>
				) : recentVerified.length === 0 ? (
					<div className="px-4 py-10 text-center">
						<FileText
							size={32}
							className="mx-auto mb-2 text-zinc-700"
						/>
						<p className="text-sm text-zinc-400">
							No verified loan records yet.
						</p>
						<p className="mt-1 text-xs text-zinc-500">
							Once clean loans are ingested or reviewers approve
							exceptions, verified golden records will appear
							here.
						</p>
					</div>
				) : (
					<div className="overflow-x-auto">
						<table className="w-full text-xs">
							<thead className="border-b border-zinc-800">
								<tr>
									{[
										'Loan ID',
										'Borrower',
										'Type',
										'Principal',
										'Current Balance',
										'Rate',
										'State',
										'Verified Date',
										'Hash',
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
								{recentVerified.map((loan) => (
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
										<td className="px-4 py-2.5 text-zinc-500">
											{formatIndianDate(loan.verified_at)}
										</td>
										<td
											className="max-w-[90px] truncate px-4 py-2.5 font-mono text-[10px] text-zinc-500"
											title={loan.record_hash}
										>
											{loan.record_hash
												? `${loan.record_hash.slice(0, 10)}…`
												: '—'}
										</td>
									</tr>
								))}
							</tbody>
						</table>
					</div>
				)}
			</div>
		</div>
	);
}
