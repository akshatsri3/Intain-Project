import { useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { datasetService } from '../services/datasetService';
import { formatIndianNumber, formatIndianDateTime } from '../utils/formatters';
import {
	Upload,
	FileText,
	X,
	CheckCircle,
	AlertTriangle,
	ChevronDown,
} from 'lucide-react';

const SOURCE_TYPES = [
	{ value: 'LOAN_TAPE', label: 'Loan Tape' },
	{ value: 'SERVICER_UPDATE', label: 'Servicer Update' },
	{ value: 'DOCUMENT_MANIFEST', label: 'Document Manifest' },
	{ value: 'OTHER', label: 'Other' },
];

function formatBytes(bytes) {
	if (bytes === 0) return '0 B';
	const k = 1024;
	const sizes = ['B', 'KB', 'MB'];
	const i = Math.floor(Math.log(bytes) / Math.log(k));
	return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

export default function UploadDataset() {
	const [file, setFile] = useState(null);
	const [sourceType, setSourceType] = useState('LOAN_TAPE');
	const [dragging, setDragging] = useState(false);
	const [uploading, setUploading] = useState(false);
	const [uploadStep, setUploadStep] = useState('');
	const [result, setResult] = useState(null);
	const [error, setError] = useState('');

	const fileInputRef = useRef(null);
	const navigate = useNavigate();

	const acceptFile = (f) => {
		if (!f) return;
		if (!f.name.endsWith('.csv')) {
			setError('Only CSV files are supported.');
			return;
		}
		setFile(f);
		setError('');
		setResult(null);
	};

	const onDrop = useCallback((e) => {
		e.preventDefault();
		setDragging(false);
		acceptFile(e.dataTransfer.files[0]);
	}, []);

	const onDragOver = (e) => {
		e.preventDefault();
		setDragging(true);
	};
	const onDragLeave = () => setDragging(false);

	const handleUpload = async () => {
		if (!file) return;
		setError('');
		setUploading(true);
		setResult(null);

		try {
			setUploadStep('Uploading file...');
			await new Promise((r) => setTimeout(r, 400));
			setUploadStep('Parsing records...');
			await new Promise((r) => setTimeout(r, 300));
			setUploadStep('Normalizing data & running validation...');

			const data = await datasetService.upload(file, sourceType);
			setResult(data);
		} catch (err) {
			setError(
				err.response?.data?.detail ||
					'Upload failed. Please try again.',
			);
		} finally {
			setUploading(false);
			setUploadStep('');
		}
	};

	return (
		<div className="mx-auto max-w-2xl space-y-6">
			<div>
				<h2 className="text-xl font-bold tracking-tight text-white">
					Upload Dataset
				</h2>
				<p className="mt-0.5 text-sm text-zinc-400">
					Upload a CSV file to ingest, normalize, and validate loan
					records.
				</p>
			</div>

			{!result ? (
				<div className="card space-y-5">
					{/* Drop zone */}
					<div
						id="dropzone"
						onDrop={onDrop}
						onDragOver={onDragOver}
						onDragLeave={onDragLeave}
						onClick={() => fileInputRef.current?.click()}
						className={`cursor-pointer rounded-xl border-2 border-dashed p-10 text-center transition-all ${
							dragging
								? 'border-white bg-zinc-900/60'
								: 'border-zinc-800 bg-zinc-950/40 hover:border-zinc-600'
						}`}
					>
						<input
							ref={fileInputRef}
							id="file-input"
							type="file"
							accept=".csv"
							className="hidden"
							onChange={(e) => acceptFile(e.target.files[0])}
						/>
						<Upload
							size={32}
							className="mx-auto mb-3 text-zinc-500"
						/>
						<p className="text-sm font-medium text-zinc-200">
							Drag & drop your CSV file here
						</p>
						<p className="mt-1 text-xs text-zinc-500">
							or click to browse from your device
						</p>
						<p className="mt-3 text-xs text-zinc-600">
							Supported format: .csv only
						</p>
					</div>

					{/* Selected file info */}
					{file && (
						<div className="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3">
							<FileText
								size={18}
								className="shrink-0 text-zinc-200"
							/>
							<div className="min-w-0 flex-1">
								<p className="truncate text-sm font-medium text-zinc-200">
									{file.name}
								</p>
								<p className="text-xs text-zinc-500">
									{formatBytes(file.size)}
								</p>
							</div>
							<button
								onClick={() => setFile(null)}
								className="text-zinc-500 hover:text-zinc-300"
							>
								<X size={15} />
							</button>
						</div>
					)}

					{/* Source type */}
					<div className="space-y-2">
						<label
							htmlFor="source-type"
							className="text-sm font-medium text-zinc-300"
						>
							Source Type
						</label>
						<div className="relative">
							<select
								id="source-type"
								value={sourceType}
								onChange={(e) => setSourceType(e.target.value)}
								className="input-field appearance-none pr-8"
							>
								{SOURCE_TYPES.map(({ value, label }) => (
									<option
										key={value}
										value={value}
										className="bg-zinc-900 text-zinc-100"
									>
										{label}
									</option>
								))}
							</select>
							<ChevronDown
								size={14}
								className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-zinc-500"
							/>
						</div>
					</div>

					{/* Error */}
					{error && (
						<div className="flex items-center gap-2 rounded-lg border border-red-800/80 bg-red-950/60 px-4 py-3 text-sm text-red-300">
							<AlertTriangle size={14} />
							<span>{error}</span>
						</div>
					)}

					{/* Upload button / progress */}
					{uploading ? (
						<div className="flex items-center gap-3 py-2 text-sm text-zinc-200">
							<div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
							<span>{uploadStep}</span>
						</div>
					) : (
						<button
							id="upload-submit-btn"
							onClick={handleUpload}
							disabled={!file}
							className="btn-primary flex w-full items-center justify-center gap-2"
						>
							<Upload size={15} />
							Upload and Process
						</button>
					)}
				</div>
			) : (
				/* Import Summary */
				<ImportSummary
					result={result}
					onViewDetails={() =>
						navigate(`/datasets/${result.dataset.id}`)
					}
					onUploadAnother={() => {
						setResult(null);
						setFile(null);
					}}
				/>
			)}
		</div>
	);
}

function ImportSummary({ result, onViewDetails, onUploadAnother }) {
	const { dataset, normalization_summary: ns } = result;
	const successRate =
		dataset.total_rows > 0
			? Math.round(
					(dataset.successfully_imported_rows / dataset.total_rows) *
						100,
				)
			: 0;

	return (
		<div className="space-y-4">
			<div className="flex items-center gap-2 text-emerald-400">
				<CheckCircle size={20} />
				<h3 className="font-semibold text-white">
					Import & Normalization Complete
				</h3>
			</div>

			<div className="card space-y-4">
				<div className="flex items-start justify-between">
					<div>
						<p className="text-base font-semibold text-white">
							{dataset.file_name}
						</p>
						<p className="mt-0.5 text-xs text-zinc-400">
							{dataset.source_type} ·{' '}
							{formatIndianDateTime(dataset.uploaded_at)}
						</p>
					</div>
					<span className="badge badge-green">{dataset.status}</span>
				</div>

				{/* Row counts */}
				<div className="grid grid-cols-3 gap-3">
					<div className="rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-center">
						<p className="font-mono text-2xl font-bold text-white">
							{formatIndianNumber(dataset.total_rows)}
						</p>
						<p className="mt-0.5 text-xs text-zinc-500">
							Total Rows
						</p>
					</div>
					<div className="rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-center">
						<p className="font-mono text-2xl font-bold text-emerald-400">
							{formatIndianNumber(
								dataset.successfully_imported_rows,
							)}
						</p>
						<p className="mt-0.5 text-xs text-zinc-500">Imported</p>
					</div>
					<div className="rounded-lg border border-zinc-800 bg-zinc-900 p-3 text-center">
						<p className="font-mono text-2xl font-bold text-amber-400">
							{formatIndianNumber(dataset.failed_rows)}
						</p>
						<p className="mt-0.5 text-xs text-zinc-500">Failed</p>
					</div>
				</div>

				{/* Progress bar */}
				<div>
					<div className="mb-1 flex justify-between text-xs text-zinc-500">
						<span>Success rate</span>
						<span className="font-mono text-zinc-300">
							{successRate}%
						</span>
					</div>
					<div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
						<div
							className="h-full rounded-full bg-white transition-all"
							style={{ width: `${successRate}%` }}
						/>
					</div>
				</div>
			</div>

			{/* Normalization summary */}
			<div className="card">
				<h4 className="section-title mb-3">Normalization Counters</h4>
				<div className="space-y-2.5">
					{[
						{
							label: 'Date formats normalized',
							value: formatIndianNumber(ns.dates_normalized),
						},
						{
							label: 'Currency values normalized',
							value: formatIndianNumber(
								ns.currency_values_normalized,
							),
						},
						{
							label: 'Interest rates normalized',
							value: formatIndianNumber(
								ns.interest_rates_normalized,
							),
						},
						{
							label: 'Missing values converted to null',
							value: formatIndianNumber(
								ns.missing_values_converted_to_null,
							),
						},
					].map(({ label, value }) => (
						<div
							key={label}
							className="flex items-center justify-between text-sm"
						>
							<span className="text-zinc-400">{label}</span>
							<span className="font-mono font-semibold text-zinc-200">
								{value}
							</span>
						</div>
					))}
				</div>
			</div>

			<div className="flex gap-3">
				<button
					id="view-details-btn"
					onClick={onViewDetails}
					className="btn-primary flex-1"
				>
					View Dataset Details
				</button>
				<button
					onClick={onUploadAnother}
					className="btn-secondary flex-1"
				>
					Upload Another
				</button>
			</div>
		</div>
	);
}
