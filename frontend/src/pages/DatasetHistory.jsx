import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetService } from '../services/datasetService';
import { formatIndianNumber, formatIndianDate } from '../utils/formatters';
import { Upload, Database } from 'lucide-react';

const STATUS_BADGE = {
	COMPLETED: 'badge badge-green',
	PROCESSING: 'badge badge-amber',
	FAILED: 'badge badge-red',
	UPLOADED: 'badge badge-slate',
};

export default function DatasetHistory() {
	const [datasets, setDatasets] = useState([]);
	const [loading, setLoading] = useState(true);
	const navigate = useNavigate();

	useEffect(() => {
		datasetService
			.list()
			.then(setDatasets)
			.catch(console.error)
			.finally(() => setLoading(false));
	}, []);

	return (
		<div className="space-y-5">
			<div className="flex items-center justify-between">
				<div>
					<h2 className="text-xl font-bold tracking-tight text-white">
						Dataset History
					</h2>
					<p className="mt-0.5 text-sm text-zinc-400">
						All CSV datasets you have uploaded.
					</p>
				</div>
				<button
					id="history-upload-btn"
					onClick={() => navigate('/upload')}
					className="btn-primary flex items-center gap-2"
				>
					<Upload size={14} />
					Upload New
				</button>
			</div>

			<div className="card overflow-hidden p-0">
				{loading ? (
					<p className="p-6 text-sm text-zinc-500">
						Loading datasets...
					</p>
				) : datasets.length === 0 ? (
					<div className="px-6 py-14 text-center">
						<Database
							size={36}
							className="mx-auto mb-3 text-zinc-700"
						/>
						<p className="text-sm font-medium text-zinc-400">
							No datasets yet
						</p>
						<p className="mt-1 text-xs text-zinc-500">
							Upload your first loan tape CSV to see it listed
							here.
						</p>
						<button
							onClick={() => navigate('/upload')}
							className="btn-primary mt-4 inline-flex items-center gap-2"
						>
							<Upload size={14} /> Upload Dataset
						</button>
					</div>
				) : (
					<div className="overflow-x-auto">
						<table className="w-full text-xs">
							<thead className="border-b border-zinc-800">
								<tr>
									{[
										'File Name',
										'Source Type',
										'Upload Date',
										'Total Rows',
										'Imported',
										'Failed',
										'Status',
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
								{datasets.map((d) => (
									<tr
										key={d.id}
										className="transition-colors hover:bg-zinc-900/40"
									>
										<td className="max-w-[200px] truncate px-4 py-3 font-medium text-zinc-200">
											{d.file_name}
										</td>
										<td className="px-4 py-3">
											<span className="badge badge-slate">
												{d.source_type}
											</span>
										</td>
										<td className="px-4 py-3 text-zinc-400">
											{formatIndianDate(d.uploaded_at)}
										</td>
										<td className="px-4 py-3 font-mono text-zinc-300">
											{formatIndianNumber(d.total_rows)}
										</td>
										<td className="px-4 py-3 font-mono text-emerald-400">
											{formatIndianNumber(
												d.successfully_imported_rows,
											)}
										</td>
										<td className="px-4 py-3 font-mono text-amber-400">
											{formatIndianNumber(d.failed_rows)}
										</td>
										<td className="px-4 py-3">
											<span
												className={
													STATUS_BADGE[d.status] ||
													'badge badge-slate'
												}
											>
												{d.status}
											</span>
										</td>
										<td className="px-4 py-3 text-right">
											<button
												id={`view-dataset-${d.id}`}
												onClick={() =>
													navigate(
														`/datasets/${d.id}`,
													)
												}
												className="text-xs font-medium text-zinc-300 transition-colors hover:text-white"
											>
												View Details →
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
