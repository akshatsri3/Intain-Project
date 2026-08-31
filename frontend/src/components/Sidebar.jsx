import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
	LayoutDashboard,
	Upload,
	History,
	AlertTriangle,
	CheckCircle,
	Clock,
	LogOut,
	ShieldCheck,
} from 'lucide-react';

const NAV_BY_ROLE = {
	DATA_OPERATOR: [
		{ to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
		{ to: '/upload', icon: Upload, label: 'Upload Dataset' },
		{ to: '/datasets', icon: History, label: 'Dataset History' },
		{ to: '/audit', icon: Clock, label: 'Audit Trail' },
	],
	REVIEWER: [
		{ to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
		{ to: '/exceptions', icon: AlertTriangle, label: 'Exception Queue' },
		{ to: '/verified', icon: CheckCircle, label: 'Verified Loans' },
		{ to: '/audit', icon: Clock, label: 'Audit Trail' },
	],
	DATA_CONSUMER: [
		{ to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
		{ to: '/verified', icon: CheckCircle, label: 'Verified Loans' },
		{ to: '/audit', icon: Clock, label: 'Audit Trail' },
	],
};

export default function Sidebar() {
	const { user, logout } = useAuth();
	const navigate = useNavigate();

	const navItems = NAV_BY_ROLE[user?.role] || [];

	const handleLogout = () => {
		logout();
		navigate('/login');
	};

	return (
		<aside className="flex min-h-screen w-64 shrink-0 flex-col border-r border-zinc-800/80 bg-black">
			{/* Logo */}
			<div className="border-b border-zinc-800/80 px-6 py-5">
				<div className="flex items-center gap-3">
					<div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white shadow-sm">
						<ShieldCheck size={18} className="text-black" />
					</div>
					<div>
						<p className="text-sm leading-tight font-bold tracking-tight text-white">
							Loan Copilot
						</p>
						<p className="text-xs font-medium text-zinc-500">
							Data Verification
						</p>
					</div>
				</div>
			</div>

			{/* Navigation */}
			<nav className="flex-1 space-y-1 px-3 py-4">
				{navItems.map(({ to, icon: Icon, label }) => (
					<NavLink
						key={to}
						to={to}
						className={({ isActive }) =>
							`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-150 ${
								isActive
									? 'bg-white font-semibold text-black shadow-sm'
									: 'font-medium text-zinc-400 hover:bg-zinc-900 hover:text-zinc-100'
							}`
						}
					>
						<Icon size={16} />
						<span className="flex-1">{label}</span>
					</NavLink>
				))}
			</nav>

			{/* Logout */}
			<div className="border-t border-zinc-800/80 px-3 py-4">
				<button
					id="sidebar-logout-btn"
					onClick={handleLogout}
					className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-zinc-400 transition-colors hover:bg-zinc-900 hover:text-zinc-100"
				>
					<LogOut size={16} />
					Sign Out
				</button>
			</div>
		</aside>
	);
}
