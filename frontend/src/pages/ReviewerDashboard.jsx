import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { validationService } from '../services/validationService';
import { reviewService } from '../services/reviewService';
import { formatIndianNumber, formatIndianDate } from '../utils/formatters';
import {
	AlertTriangle,
	Brain,
	Clock,
	CheckCircle,
	Shield,
	ArrowRight,
	XCircle,
} from 'lucide-react';

function StatCard({ icon: Icon, label, value, color, onClick }) {
	return (
		<button
			onClick={onClick}
			className="card flex w-full items-center gap-4 text-left transition-colors hover:border-zinc-700"
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

export default function ReviewerDashboard() {
	const { user } = useAuth();
	const navigate = useNavigate();
	const [stats, setStats] = useState(null);
	const [recentExceptions, setRecentExceptions] = useState([]);
	const [recentDecisions, setRecentDecisions] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchData = async () => {
			try {
				const [st, excs, decs] = await Promise.all([
					validationService.getStats(),
					validationService.getExceptions({
						status: 'OPEN',
						limit: 5,
					}),
					reviewService.getDecisions(5, 0),
				]);
				setStats(st);
				setRecentExceptions(excs);
				setRecentDecisions(decs);
			} catch (e) {
				console.error(e);
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, []);

	return (
		<div className="space-y-6">
			{/* Welcome */}
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-xl font-bold tracking-tight text-white">
						Welcome back, {user?.name?.split(' ')[0]}
					</h2>
					<p className="mt-0.5 text-sm text-zinc-400">
						Review flagged loan records and resolve data exceptions.
					</p>
				</div>
				<button
					id="go-to-exceptions-btn"
					onClick={() => navigate('/exceptions')}
					className="btn-primary flex items-center gap-2"
				>
					<AlertTriangle size={15} /> Exception Queue
				</button>
			</div>

			{/* Stats */}
			{stats && (
				<div className="grid grid-cols-2 gap-3 md:grid-cols-4">
					<StatCard
						icon={AlertTriangle}
						label="Open Exceptions"
						value={formatIndianNumber(stats.open)}
						color="bg-amber-950/70 border border-amber-800/50"
						onClick={() => navigate('/exceptions')}
					/>
					<StatCard
						icon={CheckCircle}
						label="Resolved"
						value={formatIndianNumber(stats.resolved)}
						color="bg-emerald-950/70 border border-emerald-800/50"
						onClick={() => navigate('/exceptions')}
					/>
					<StatCard
						icon={XCircle}
						label="Errors"
						value={formatIndianNumber(stats.errors)}
						color="bg-red-950/70 border border-red-800/50"
						onClick={() => navigate('/exceptions')}
					/>
					<StatCard
						icon={Shield}
						label="Total Exceptions"
						value={formatIndianNumber(stats.total)}
						color="bg-zinc-800 border border-zinc-700"
						onClick={() => navigate('/exceptions')}
					/>
				</div>
			)}

			{/* Recent Exceptions */}
			<div className="card">
				<div className="mb-4 flex items-center justify-between">
					<h3 className="section-title flex items-center gap-2">
						<AlertTriangle size={16} className="text-amber-400" />{' '}
						Pending Review
					</h3>
					<button
						onClick={() => navigate('/exceptions')}
						className="flex items-center gap-1 text-sm text-zinc-400 hover:text-white"
					>
						View all <ArrowRight size={13} />
					</button>
				</div>

				{loading ? (
					<p className="py-4 text-sm text-zinc-500">Loading...</p>
				) : recentExceptions.length === 0 ? (
					<div className="py-6 text-center">
						<CheckCircle
							size={28}
							className="mx-auto mb-2 text-emerald-500"
						/>
						<p className="text-sm text-zinc-500">
							All exceptions have been reviewed!
						</p>
					</div>
				) : (
					<div className="space-y-2">
						{recentExceptions.map((exc) => (
							<div
								key={exc.id}
								className="flex items-center gap-3 rounded-lg border border-zinc-800/60 bg-zinc-900/60 px-3.5 py-2.5 transition-colors hover:bg-zinc-900"
							>
								<span
									className={`badge text-[10px] ${
										exc.severity === 'ERROR'
											? 'badge-red'
											: exc.severity === 'WARNING'
												? 'badge-amber'
												: 'badge-blue'
									}`}
								>
									{exc.severity}
								</span>
								<span className="flex-1 truncate text-sm font-medium text-zinc-200">
									{exc.rule_code.replace(/_/g, ' ')}
								</span>
								<span className="font-mono text-xs text-zinc-500">
									{exc.loan_loan_id || `Loan #${exc.loan_id}`}
								</span>
								{exc.ai_suggestion && (
									<Brain
										size={13}
										className="text-purple-400"
										title="AI suggestion available"
									/>
								)}
							</div>
						))}
					</div>
				)}
			</div>

			{/* Recent Decisions */}
			<div className="card">
				<h3 className="section-title mb-4 flex items-center gap-2">
					<Clock size={16} className="text-zinc-300" /> Recent
					Decisions
				</h3>
				{recentDecisions.length === 0 ? (
					<p className="py-4 text-sm text-zinc-500">
						No review decisions yet.
					</p>
				) : (
					<div className="space-y-2">
						{recentDecisions.map((dec) => (
							<div
								key={dec.id}
								className="flex items-center gap-3 rounded-lg border border-zinc-800/60 bg-zinc-900/60 px-3.5 py-2.5"
							>
								<span
									className={`badge text-[10px] ${
										dec.decision === 'ACCEPT_SUGGESTION'
											? 'badge-green'
											: dec.decision === 'REJECT_LOAN'
												? 'badge-red'
												: dec.decision ===
													  'MANUAL_OVERRIDE'
													? 'badge-blue'
													: 'badge-amber'
									}`}
								>
									{dec.decision.replace(/_/g, ' ')}
								</span>
								<span className="flex-1 text-sm text-zinc-300">
									Exception #{dec.exception_id}
								</span>
								<span className="font-mono text-xs text-zinc-500">
									{formatIndianDate(dec.decided_at)}
								</span>
							</div>
						))}
					</div>
				)}
			</div>
		</div>
	);
}
