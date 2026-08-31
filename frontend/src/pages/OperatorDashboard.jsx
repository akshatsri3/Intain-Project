import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { datasetService } from '../services/datasetService';
import { formatIndianNumber } from '../utils/formatters';
import {
	Upload,
	Database,
	AlertTriangle,
	CheckCircle,
	ArrowRight,
} from 'lucide-react';

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
				<p className="text-2xl font-bold text-white">{value}</p>
			</div>
		</div>
	);
}

const STATUS_BADGE = {
	COMPLETED: 'badge badge-green',
	PROCESSING: 'badge badge-amber',
	FAILED: 'badge badge-red',
	UPLOADED: 'badge badge-slate',
};

export default function OperatorDashboard() {
	const { user } = useAuth();
	const navigate = useNavigate();
	const [datasets, setDatasets] = useState([]);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		datasetService
			.list()
			.then(setDatasets)
			.catch(console.error)
			.finally(() => setLoading(false));
	}, []);

	const totalRecords = datasets.reduce(
		(s, d) => s + (d.successfully_imported_rows || 0),
		0,
	);
	const totalFailed = datasets.reduce((s, d) => s + (d.failed_rows || 0), 0);
	const recent = datasets.slice(0, 5);

	return (
		<div className="space-y-6">
			{/* Welcome */}
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-xl font-bold tracking-tight text-white">
						Welcome back, {user?.name?.split(' ')[0]}
					</h2>
					<p className="mt-0.5 text-sm text-zinc-400">
						Here's an overview of your data ingestion activity.
					</p>
				</div>
				<button
					id="dashboard-upload-btn"
					onClick={() => navigate('/upload')}
					className="btn-primary flex items-center gap-2"
				>
					<Upload size={15} />
					Upload Dataset
				</button>
			</div>

			{/* Stats */}
			<div className="grid grid-cols-1 gap-4 md:grid-cols-3">
				<StatCard
					icon={Database}
					label="Datasets Uploaded"
					value={formatIndianNumber(datasets.length)}
					color="bg-zinc-800 border border-zinc-700"
				/>
				<StatCard
					icon={CheckCircle}
					label="Records Imported"
					value={formatIndianNumber(totalRecords)}
					color="bg-emerald-950/70 border border-emerald-800/50"
				/>
				<StatCard
					icon={AlertTriangle}
					label="Failed Imports"
					value={formatIndianNumber(totalFailed)}
					color="bg-amber-950/70 border border-amber-800/50"
				/>
			</div>

			{/* Recent uploads */}
			<div className="card overflow-hidden p-0">
				<div className="flex items-center justify-between border-b border-zinc-800/80 p-5">
					<h3 className="section-title">Recent Uploads</h3>
					<button
						onClick={() => navigate('/datasets')}
						className="flex items-center gap-1 text-sm text-zinc-300 hover:text-white"
					>
						View all <ArrowRight size={13} />
					</button>
				</div>

				{loading ? (
					<p className="p-5 text-sm text-zinc-500">Loading...</p>
				) : recent.length === 0 ? (
					<div className="px-4 py-10 text-center">
						<Database
							size={32}
							className="mx-auto mb-3 text-zinc-700"
						/>
						<p className="text-sm text-zinc-400">
							No datasets uploaded yet.
						</p>
						<button
							onClick={() => navigate('/upload')}
							className="btn-primary mt-4 inline-flex items-center gap-2"
						>
							<Upload size={14} /> Upload your first dataset
						</button>
					</div>
				) : (
					<div className="overflow-x-auto">
						<table className="w-full text-xs">
							<thead className="border-b border-zinc-800">
								<tr>
									<th className="table-header px-4 py-3 text-left">
										File
									</th>
									<th className="table-header px-4 py-3 text-left">
										Source
									</th>
									<th className="table-header px-4 py-3 text-right">
										Imported
									</th>
									<th className="table-header px-4 py-3 text-right">
										Failed
									</th>
									<th className="table-header px-4 py-3 text-left">
										Status
									</th>
									<th className="table-header px-4 py-3"></th>
								</tr>
							</thead>
							<tbody className="divide-y divide-zinc-800/80">
								{recent.map((d) => (
									<tr
										key={d.id}
										className="transition-colors hover:bg-zinc-900/40"
									>
										<td className="table-cell max-w-[180px] truncate font-medium text-zinc-200">
											{d.file_name}
										</td>
										<td className="table-cell">
											<span className="badge badge-slate">
												{d.source_type}
											</span>
										</td>
										<td className="table-cell text-right font-mono text-emerald-400">
											{formatIndianNumber(
												d.successfully_imported_rows,
											)}
										</td>
										<td className="table-cell text-right font-mono text-amber-400">
											{formatIndianNumber(d.failed_rows)}
										</td>
										<td className="table-cell">
											<span
												className={
													STATUS_BADGE[d.status] ||
													'badge badge-slate'
												}
											>
												{d.status}
											</span>
										</td>
										<td className="table-cell text-right">
											<button
												onClick={() =>
													navigate(
														`/datasets/${d.id}`,
													)
												}
												className="text-xs text-zinc-400 transition-colors hover:text-white"
											>
												View →
											</button>
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
