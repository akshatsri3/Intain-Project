import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { datasetService } from '../services/datasetService';
import {
	formatCurrency,
	formatIndianNumber,
	formatIndianDateTime,
} from '../utils/formatters';
import { ArrowLeft, AlertTriangle, FileText } from 'lucide-react';

const STATUS_BADGE = {
	COMPLETED: 'badge badge-green',
	PROCESSING: 'badge badge-amber',
	FAILED: 'badge badge-red',
	UPLOADED: 'badge badge-slate',
};

const TABS = ['Overview', 'Records', 'Import Errors'];

function InfoRow({ label, value }) {
	return (
		<div className="flex items-center justify-between border-b border-zinc-800/80 py-2.5 last:border-0">
			<span className="text-sm text-zinc-400">{label}</span>
			<span className="text-sm font-medium text-zinc-200">{value}</span>
		</div>
	);
}

export default function DatasetDetails() {
	const { id } = useParams();
	const navigate = useNavigate();
	const [dataset, setDataset] = useState(null);
	const [errors, setErrors] = useState([]);
	const [records, setRecords] = useState([]);
	const [activeTab, setActiveTab] = useState('Overview');
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchAll = async () => {
			try {
				const [ds, errs, recs] = await Promise.all([
					datasetService.getById(id),
					datasetService.getErrors(id),
					datasetService.getRecords(id, 20, 0),
				]);
				setDataset(ds);
				setErrors(errs);
				setRecords(recs);
			} catch (e) {
				console.error(e);
			} finally {
				setLoading(false);
			}
		};
		fetchAll();
	}, [id]);

	if (loading) {
		return (
			<div className="p-6 text-sm text-zinc-500">Loading dataset...</div>
		);
	}

	if (!dataset) {
		return (
			<div className="p-6 text-sm text-red-400">Dataset not found.</div>
		);
	}

	return (
		<div className="space-y-5">
			{/* Header */}
			<div className="flex items-center gap-3">
				<button
					onClick={() => navigate('/datasets')}
					className="text-zinc-500 transition-colors hover:text-zinc-200"
				>
					<ArrowLeft size={18} />
				</button>
				<div className="flex-1">
					<div className="flex items-center gap-2">
						<h2 className="truncate text-xl font-bold tracking-tight text-white">
							{dataset.file_name}
						</h2>
						<span
							className={
								STATUS_BADGE[dataset.status] ||
								'badge badge-slate'
							}
						>
							{dataset.status}
						</span>
					</div>
					<p className="mt-0.5 text-xs text-zinc-400">
						{dataset.source_type} · Uploaded{' '}
						{new Date(dataset.uploaded_at).toLocaleString()}
					</p>
				</div>
			</div>

			{/* Tabs */}
			<div className="flex w-fit gap-1 rounded-lg border border-zinc-800 bg-zinc-950 p-1">
				{TABS.map((tab) => (
					<button
						key={tab}
						id={`tab-${tab.toLowerCase().replace(' ', '-')}`}
						onClick={() => setActiveTab(tab)}
						className={`rounded-md px-4 py-1.5 text-sm font-medium transition-all ${
							activeTab === tab
								? 'bg-white font-semibold text-black shadow-sm'
								: 'text-zinc-400 hover:text-zinc-200'
						}`}
					>
						{tab}
						{tab === 'Import Errors' && errors.length > 0 && (
							<span className="ml-1.5 rounded-full border border-amber-800 bg-amber-950 px-1.5 py-0.5 text-xs text-amber-300">
								{errors.length}
							</span>
						)}
					</button>
				))}
			</div>

			{/* Tab Content */}
			{activeTab === 'Overview' && (
				<div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
					<div className="card">
						<h3 className="section-title mb-3">Dataset Metadata</h3>
						<InfoRow label="File Name" value={dataset.file_name} />
						<InfoRow
							label="Source Type"
							value={dataset.source_type}
						/>
						<InfoRow
							label="Upload Date"
							value={formatIndianDateTime(dataset.uploaded_at)}
						/>
						<InfoRow
							label="File Size"
							value={
								dataset.file_size
									? `${(dataset.file_size / 1024).toFixed(1)} KB`
									: '—'
							}
						/>
						<InfoRow label="Status" value={dataset.status} />
					</div>

					<div className="card">
						<h3 className="section-title mb-3">Import Summary</h3>
						<InfoRow
							label="Total Rows"
							value={formatIndianNumber(dataset.total_rows)}
						/>
						<InfoRow
							label="Successfully Imported"
							value={formatIndianNumber(
								dataset.successfully_imported_rows,
							)}
						/>
						<InfoRow
							label="Failed Imports"
							value={formatIndianNumber(dataset.failed_rows)}
						/>
						<InfoRow
							label="Success Rate"
							value={
								dataset.total_rows > 0
									? `${Math.round((dataset.successfully_imported_rows / dataset.total_rows) * 100)}%`
									: '—'
							}
						/>
					</div>

					<div className="card lg:col-span-2">
						<h3 className="section-title mb-1">Source Lineage</h3>
						<p className="mb-3 text-xs text-zinc-500">
							Every normalized loan record in this dataset is
							traceable back to this source file via dataset_id
							and source_row_number.
						</p>
						<div className="space-y-1 rounded-lg border border-zinc-800 bg-zinc-900 p-4 font-mono text-xs text-zinc-300">
							<p>
								<span className="text-zinc-500">
									dataset_id:
								</span>{' '}
								{dataset.id}
							</p>
							<p>
								<span className="text-zinc-500">
									file_name:
								</span>{' '}
								{dataset.file_name}
							</p>
							<p>
								<span className="text-zinc-500">
									source_type:
								</span>{' '}
								{dataset.source_type}
							</p>
							<p className="pt-2 font-sans text-[11px] text-zinc-500">
								Lineage Chain: loan record → dataset_id +
								source_row_number → raw_records (JSONB)
							</p>
						</div>
					</div>
				</div>
			)}

			{activeTab === 'Records' && (
				<div className="card overflow-auto p-0">
					<div className="border-b border-zinc-800 px-5 py-4">
						<h3 className="section-title">
							Normalized Loan Records
						</h3>
						<p className="mt-0.5 text-xs text-zinc-500">
							Showing first 20 records. All values are normalized
							to internal schema.
						</p>
					</div>
					{records.length === 0 ? (
						<div className="py-10 text-center">
							<FileText
								size={28}
								className="mx-auto mb-2 text-zinc-700"
							/>
							<p className="text-sm text-zinc-500">
								No records found.
							</p>
						</div>
					) : (
						<div className="overflow-x-auto">
							<table className="w-full text-xs">
								<thead className="border-b border-zinc-800">
									<tr>
										{[
											'Row',
											'Loan ID',
											'Borrower ID',
											'Loan Type',
											'Orig. Principal',
											'Interest Rate',
											'Origination Date',
											'State',
											'Payment Status',
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
									{records.map((r) => (
										<tr
											key={r.id}
											className="transition-colors hover:bg-zinc-900/40"
										>
											<td className="px-4 py-2.5 font-mono text-zinc-500">
												{r.source_row_number}
											</td>
											<td className="px-4 py-2.5 font-medium text-zinc-200">
												{r.loan_id || '—'}
											</td>
											<td className="px-4 py-2.5 text-zinc-400">
												{r.borrower_id || '—'}
											</td>
											<td className="px-4 py-2.5 text-zinc-400">
												{r.loan_type || '—'}
											</td>
											<td className="px-4 py-2.5 font-mono text-zinc-300">
												{formatCurrency(
													r.original_principal,
												)}
											</td>
											<td className="px-4 py-2.5 font-mono text-zinc-300">
												{r.interest_rate != null
													? `${r.interest_rate}%`
													: '—'}
											</td>
											<td className="px-4 py-2.5 text-zinc-400">
												{r.origination_date || '—'}
											</td>
											<td className="px-4 py-2.5 text-zinc-400">
												{r.borrower_state || '—'}
											</td>
											<td className="px-4 py-2.5">
												{r.payment_status ? (
													<span
														className={`badge ${r.payment_status.toLowerCase().includes('past') ? 'badge-amber' : 'badge-green'}`}
													>
														{r.payment_status}
													</span>
												) : (
													'—'
												)}
											</td>
										</tr>
									))}
								</tbody>
							</table>
						</div>
					)}
				</div>
			)}

			{activeTab === 'Import Errors' && (
				<div className="card overflow-hidden p-0">
					<div className="flex items-center gap-2 border-b border-zinc-800 px-5 py-4">
						<AlertTriangle size={16} className="text-amber-400" />
						<h3 className="section-title">Failed Import Rows</h3>
						<span className="ml-1 font-mono text-xs text-zinc-500">
							({errors.length} rows)
						</span>
					</div>
					{errors.length === 0 ? (
						<div className="py-10 text-center">
							<p className="text-sm text-zinc-500">
								No import errors — all rows were successfully
								normalized.
							</p>
						</div>
					) : (
						<div className="divide-y divide-zinc-800/80">
							{errors.map((err) => (
								<div key={err.id} className="px-5 py-4">
									<div className="mb-2 flex items-center gap-2">
										<span className="badge badge-amber">
											Row {err.row_number}
										</span>
										<span className="badge badge-red">
											{err.error_type}
										</span>
									</div>
									<p className="mb-2 text-xs text-red-400">
										{err.error_message}
									</p>
									{err.raw_data_json && (
										<details className="text-xs">
											<summary className="cursor-pointer text-zinc-500 hover:text-zinc-300">
												View raw data
											</summary>
											<pre className="mt-2 overflow-x-auto rounded border border-zinc-800 bg-zinc-900 p-3 font-mono text-[11px] text-zinc-400">
												{JSON.stringify(
													err.raw_data_json,
													null,
													2,
												)}
											</pre>
										</details>
									)}
								</div>
							))}
						</div>
					)}
				</div>
			)}
		</div>
	);
}
