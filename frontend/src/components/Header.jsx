import { useAuth } from '../context/AuthContext';

const ROLE_COLORS = {
	DATA_OPERATOR: 'bg-blue-950/70 border-blue-800/50 text-blue-300',
	REVIEWER: 'bg-amber-950/70 border-amber-800/50 text-amber-300',
	DATA_CONSUMER: 'bg-emerald-950/70 border-emerald-800/50 text-emerald-300',
};

const ROLE_LABELS = {
	DATA_OPERATOR: 'Data Operator',
	REVIEWER: 'Reviewer',
	DATA_CONSUMER: 'Data Consumer',
};

export default function Header({ title }) {
	const { user } = useAuth();

	return (
		<header className="flex items-center justify-between border-b border-zinc-800/80 bg-black px-6 py-4">
			<h1 className="text-lg font-semibold tracking-tight text-white">
				{title}
			</h1>
			<div className="flex items-center gap-3">
				<span
					className={`rounded-full border px-2.5 py-1 text-xs font-medium ${ROLE_COLORS[user?.role] || 'border-zinc-700 bg-zinc-900 text-zinc-300'}`}
				>
					{ROLE_LABELS[user?.role] || user?.role}
				</span>
				<div className="hidden text-right sm:block">
					<p className="text-sm leading-none font-medium text-zinc-200">
						{user?.name}
					</p>
					<p className="mt-0.5 text-xs text-zinc-500">
						{user?.email}
					</p>
				</div>
				<div className="flex h-8 w-8 items-center justify-center rounded-full border border-zinc-700/80 bg-zinc-900 shadow-sm">
					<span className="text-sm font-semibold text-zinc-200">
						{user?.name?.[0]?.toUpperCase()}
					</span>
				</div>
			</div>
		</header>
	);
}
