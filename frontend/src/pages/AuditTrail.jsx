import { useState, useEffect } from 'react';
import { auditService } from '../services/auditService';
import { formatIndianDateTime } from '../utils/formatters';
import {
	Clock,
	FileText,
	Upload,
	Shield,
	AlertTriangle,
	CheckCircle,
	Brain,
	Edit3,
	Download,
} from 'lucide-react';

const EVENT_ICONS = {
	UPLOADED: Upload,
	IMPORTED: FileText,
	NORMALIZED: FileText,
	VALIDATION_RUN: Shield,
	EXCEPTION_CREATED: AlertTriangle,
	AI_SUGGESTION_GENERATED: Brain,
	AI_SUGGESTION_ACCEPTED: Brain,
	EXCEPTION_RESOLVED: CheckCircle,
	REVIEWED: CheckCircle,
	FIELD_EDITED: Edit3,
	LOAN_APPROVED: CheckCircle,
	LOAN_REJECTED: AlertTriangle,
	FLAGGED_FOR_AUDIT: AlertTriangle,
	VERIFIED_RECORD_CREATED: Shield,
	EXPORTED: Download,
};

const EVENT_COLORS = {
	UPLOADED: 'text-zinc-200 bg-zinc-900 border border-zinc-700',
	IMPORTED: 'text-zinc-400 bg-zinc-900 border border-zinc-800',
	VALIDATION_RUN:
		'text-purple-300 bg-purple-950/70 border border-purple-800/50',
	EXCEPTION_CREATED:
		'text-amber-300 bg-amber-950/70 border border-amber-800/50',
	AI_SUGGESTION_GENERATED:
		'text-purple-300 bg-purple-950/70 border border-purple-800/50',
	AI_SUGGESTION_ACCEPTED:
		'text-emerald-300 bg-emerald-950/70 border border-emerald-800/50',
	EXCEPTION_RESOLVED:
		'text-emerald-300 bg-emerald-950/70 border border-emerald-800/50',
	REVIEWED: 'text-zinc-200 bg-zinc-900 border border-zinc-700',
	FIELD_EDITED: 'text-amber-300 bg-amber-950/70 border border-amber-800/50',
	LOAN_REJECTED: 'text-red-300 bg-red-950/70 border border-red-800/50',
	FLAGGED_FOR_AUDIT:
		'text-amber-300 bg-amber-950/70 border border-amber-800/50',
	VERIFIED_RECORD_CREATED:
		'text-emerald-300 bg-emerald-950/70 border border-emerald-800/50',
	EXPORTED: 'text-zinc-200 bg-zinc-900 border border-zinc-700',
};

export default function AuditTrail() {
	const [events, setEvents] = useState([]);
	const [loading, setLoading] = useState(true);
	const [entityFilter, setEntityFilter] = useState('');
	const [eventFilter, setEventFilter] = useState('');

	useEffect(() => {
		const fetchData = async () => {
			setLoading(true);
			try {
				const data = await auditService.getRecent({
					entityType: entityFilter || undefined,
					eventType: eventFilter || undefined,
					limit: 100,
				});
				setEvents(data);
			} catch (e) {
				console.error(e);
			} finally {
				setLoading(false);
			}
		};
		fetchData();
	}, [entityFilter, eventFilter]);

	return (
		<div className="space-y-5">
			{/* Header */}
			<div>
				<h2 className="flex items-center gap-2 text-xl font-bold tracking-tight text-white">
					<Clock size={20} className="text-white" />
					Audit Trail
				</h2>
				<p className="mt-0.5 text-sm text-zinc-400">
					Immutable chronological history of all actions across the
					loan verification pipeline.
				</p>
			</div>

			{/* Filters */}
			<div className="flex gap-3">
				<select
					id="filter-entity"
					value={entityFilter}
					onChange={(e) => setEntityFilter(e.target.value)}
					className="input-field w-auto min-w-[140px]"
				>
					<option value="" className="bg-zinc-900 text-zinc-100">
						All Entities
					</option>
					<option value="loan" className="bg-zinc-900 text-zinc-100">
						Loans
					</option>
					<option
						value="dataset"
						className="bg-zinc-900 text-zinc-100"
					>
						Datasets
					</option>
					<option
						value="exception"
						className="bg-zinc-900 text-zinc-100"
					>
						Exceptions
					</option>
				</select>
				<select
					id="filter-event-type"
					value={eventFilter}
					onChange={(e) => setEventFilter(e.target.value)}
					className="input-field w-auto min-w-[180px]"
				>
					<option value="" className="bg-zinc-900 text-zinc-100">
						All Events
					</option>
					<option
						value="UPLOADED"
						className="bg-zinc-900 text-zinc-100"
					>
						Uploaded
					</option>
					<option
						value="IMPORTED"
						className="bg-zinc-900 text-zinc-100"
					>
						Imported
					</option>
					<option
						value="VALIDATION_RUN"
						className="bg-zinc-900 text-zinc-100"
					>
						Validation Run
					</option>
					<option
						value="EXCEPTION_CREATED"
						className="bg-zinc-900 text-zinc-100"
					>
						Exception Created
					</option>
					<option
						value="AI_SUGGESTION_GENERATED"
						className="bg-zinc-900 text-zinc-100"
					>
						AI Suggestion
					</option>
					<option
						value="REVIEWED"
						className="bg-zinc-900 text-zinc-100"
					>
						Reviewed
					</option>
					<option
						value="FIELD_EDITED"
						className="bg-zinc-900 text-zinc-100"
					>
						Field Edited
					</option>
					<option
						value="VERIFIED_RECORD_CREATED"
						className="bg-zinc-900 text-zinc-100"
					>
						Verified
					</option>
					<option
						value="EXPORTED"
						className="bg-zinc-900 text-zinc-100"
					>
						Exported
					</option>
				</select>
			</div>

			{/* Timeline */}
			{loading ? (
				<p className="py-6 text-sm text-zinc-500">
					Loading audit events...
				</p>
			) : events.length === 0 ? (
				<div className="card py-10 text-center">
					<Clock size={32} className="mx-auto mb-3 text-zinc-700" />
					<p className="text-sm text-zinc-400">
						No audit events found.
					</p>
				</div>
			) : (
				<div className="relative">
					{/* Timeline line */}
					<div className="absolute top-0 bottom-0 left-5 w-px bg-zinc-800" />

					<div className="space-y-2">
						{events.map((evt) => {
							const Icon = EVENT_ICONS[evt.event_type] || Clock;
							const colorClass =
								EVENT_COLORS[evt.event_type] ||
								'text-zinc-400 bg-zinc-900 border border-zinc-800';

							return (
								<div
									key={evt.id}
									className="relative flex items-start gap-4 pl-2"
								>
									{/* Icon node */}
									<div
										className={`z-10 flex h-7 w-7 shrink-0 items-center justify-center rounded-full ${colorClass}`}
									>
										<Icon size={13} />
									</div>

									{/* Content */}
									<div className="card flex-1 px-4 py-3 transition-colors hover:border-zinc-700">
										<div className="mb-1 flex items-center justify-between">
											<div className="flex items-center gap-2">
												<span className="text-sm font-semibold text-zinc-100">
													{evt.event_type.replace(
														/_/g,
														' ',
													)}
												</span>
												<span className="badge badge-slate font-mono text-[10px]">
													{evt.entity_type}#
													{evt.entity_id}
												</span>
											</div>
											<span className="font-mono text-xs text-zinc-500">
												{formatIndianDateTime(
													evt.created_at,
												)}
											</span>
										</div>

										{evt.actor_role && (
											<p className="text-xs text-zinc-400">
												Actor:{' '}
												<span className="font-medium text-zinc-200">
													{evt.actor_role}
												</span>
												{evt.actor_id && (
													<span className="font-mono text-zinc-500">
														{' '}
														(ID #{evt.actor_id})
													</span>
												)}
											</p>
										)}

										{evt.details_json && (
											<details className="mt-2">
												<summary className="cursor-pointer text-xs text-zinc-500 hover:text-zinc-300">
													View details payload
												</summary>
												<pre className="mt-1.5 overflow-x-auto rounded border border-zinc-800 bg-zinc-900 p-2 font-mono text-[10px] text-zinc-400">
													{JSON.stringify(
														evt.details_json,
														null,
														2,
													)}
												</pre>
											</details>
										)}
									</div>
								</div>
							);
						})}
					</div>
				</div>
			)}
		</div>
	);
}
