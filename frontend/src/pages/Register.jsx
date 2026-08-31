import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
	ShieldCheck,
	Eye,
	EyeOff,
	AlertCircle,
	CheckCircle2,
	Upload,
	ClipboardCheck,
	BarChart2,
} from 'lucide-react';
import { authService } from '../services/authService';

// Role definitions shown in the selector cards
const ROLES = [
	{
		value: 'DATA_OPERATOR',
		label: 'Data Operator',
		description: 'Upload and manage loan datasets.',
		icon: Upload,
		color: 'border-blue-800/50 bg-blue-950/30 text-blue-300',
		activeColor: 'border-blue-500 bg-blue-950/60 ring-1 ring-blue-500',
	},
	{
		value: 'REVIEWER',
		label: 'Reviewer',
		description: 'Review validation exceptions and approve or reject records.',
		icon: ClipboardCheck,
		color: 'border-amber-800/50 bg-amber-950/30 text-amber-300',
		activeColor: 'border-amber-500 bg-amber-950/60 ring-1 ring-amber-500',
	},
	{
		value: 'DATA_CONSUMER',
		label: 'Data Consumer',
		description: 'View verified loan records and approved datasets.',
		icon: BarChart2,
		color: 'border-emerald-800/50 bg-emerald-950/30 text-emerald-300',
		activeColor: 'border-emerald-500 bg-emerald-950/60 ring-1 ring-emerald-500',
	},
];

export default function Register() {
	const [name, setName] = useState('');
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [confirmPassword, setConfirmPassword] = useState('');
	const [role, setRole] = useState('');
	const [showPassword, setShowPassword] = useState(false);
	const [showConfirmPassword, setShowConfirmPassword] = useState(false);
	const [error, setError] = useState('');
	const [success, setSuccess] = useState(false);
	const [loading, setLoading] = useState(false);

	const navigate = useNavigate();

	// Client-side validation before hitting the API
	const validate = () => {
		if (!name.trim()) return 'Full name is required.';
		if (!email.trim()) return 'Email address is required.';
		// Basic email format check
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return 'Please enter a valid email address.';
		if (!password) return 'Password is required.';
		if (password.length < 8) return 'Password must be at least 8 characters long.';
		if (password !== confirmPassword) return 'Passwords do not match.';
		if (!role) return 'Please select a role.';
		return null;
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');

		const validationError = validate();
		if (validationError) {
			setError(validationError);
			return;
		}

		setLoading(true);
		try {
			await authService.register(name.trim(), email.trim(), password, role);
			setSuccess(true);
			// Redirect to login after a short delay so the user can read the success message
			setTimeout(() => navigate('/login'), 2000);
		} catch (err) {
			// Log the full error to the browser console for debugging
			console.error('Registration error:', err);

			// Extract the most useful error message in priority order:
			// 1. Backend validation message  (e.g. "Email already registered")
			// 2. Backend generic detail
			// 3. Network-level message       (e.g. CORS, connection refused)
			// 4. Generic fallback
			const backendDetail = err.response?.data?.detail;
			const networkMsg = err.message;

			let displayError;
			if (backendDetail) {
				// Could be a string or a Pydantic validation array
				if (typeof backendDetail === 'string') {
					displayError = backendDetail;
				} else if (Array.isArray(backendDetail)) {
					displayError = backendDetail.map((e) => e.msg).join(', ');
				} else {
					displayError = JSON.stringify(backendDetail);
				}
			} else if (networkMsg === 'Network Error') {
				displayError =
					'Cannot reach the server. This is usually a CORS or connectivity issue — check that VITE_API_URL is set correctly and that the backend FRONTEND_URL env var includes this site.';
			} else {
				displayError = networkMsg || 'Registration failed. Please try again.';
			}

			setError(displayError);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="flex min-h-screen bg-black text-zinc-200">
			{/* Left panel — branding (matches Login page) */}
			<div className="hidden flex-col justify-between border-r border-zinc-800/80 bg-zinc-950 p-12 lg:flex lg:w-1/2">
				<div className="flex items-center gap-3">
					<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white shadow-sm">
						<ShieldCheck size={22} className="text-black" />
					</div>
					<div>
						<p className="text-lg leading-tight font-bold tracking-tight text-white">
							Loan Copilot
						</p>
						<p className="text-sm text-zinc-500">Data Verification Platform</p>
					</div>
				</div>

				<div className="max-w-lg space-y-6">
					<div>
						<h2 className="text-4xl leading-tight font-extrabold tracking-tight text-white">
							Join the Platform.
							<br />
							<span className="font-light text-zinc-400">Pick your role.</span>
						</h2>
						<p className="mt-4 text-sm leading-relaxed text-zinc-400">
							Create your account and start working with trusted loan data.
							Each role has tailored tools designed for your part of the
							verification pipeline.
						</p>
					</div>

					<div className="space-y-3 pt-2">
						{[
							'Role-based access and dashboards',
							'Secure JWT authentication',
							'Immutable audit trail for all actions',
							'AI-assisted exception resolution',
						].map((f) => (
							<div key={f} className="flex items-center gap-2.5 text-sm text-zinc-300">
								<CheckCircle2 size={16} className="shrink-0 text-white" />
								<span>{f}</span>
							</div>
						))}
					</div>
				</div>

				<p className="font-mono text-xs text-zinc-600">Intain Campus FinTech Challenge 2026</p>
			</div>

			{/* Right panel — registration form */}
			<div className="flex flex-1 items-start justify-center overflow-y-auto bg-black p-8">
				<div className="w-full max-w-md space-y-7 py-4">
					{/* Heading */}
					<div>
						<h1 className="text-2xl font-bold tracking-tight text-white">
							Create your account
						</h1>
						<p className="mt-1 text-sm text-zinc-400">
							Fill in the details below to get started
						</p>
					</div>

					{/* Success banner */}
					{success && (
						<div className="flex items-center gap-2 rounded-lg border border-emerald-800/80 bg-emerald-950/60 px-4 py-3 text-sm text-emerald-300">
							<CheckCircle2 size={16} className="shrink-0" />
							<span>
								Account created successfully! Redirecting to sign in&hellip;
							</span>
						</div>
					)}

					{/* Error banner */}
					{error && (
						<div className="flex items-center gap-2 rounded-lg border border-red-800/80 bg-red-950/60 px-4 py-3 text-sm text-red-300">
							<AlertCircle size={16} className="shrink-0" />
							<span>{error}</span>
						</div>
					)}

					<form id="register-form" onSubmit={handleSubmit} className="space-y-5" noValidate>
						{/* Full Name */}
						<div className="space-y-2">
							<label htmlFor="reg-name" className="text-sm font-medium text-zinc-300">
								Full Name
							</label>
							<input
								id="reg-name"
								type="text"
								value={name}
								onChange={(e) => setName(e.target.value)}
								required
								placeholder="Jane Smith"
								className="input-field"
								disabled={loading || success}
							/>
						</div>

						{/* Email */}
						<div className="space-y-2">
							<label htmlFor="reg-email" className="text-sm font-medium text-zinc-300">
								Email Address
							</label>
							<input
								id="reg-email"
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								required
								placeholder="jane@example.com"
								className="input-field"
								disabled={loading || success}
							/>
						</div>

						{/* Password */}
						<div className="space-y-2">
							<label htmlFor="reg-password" className="text-sm font-medium text-zinc-300">
								Password
							</label>
							<div className="relative">
								<input
									id="reg-password"
									type={showPassword ? 'text' : 'password'}
									value={password}
									onChange={(e) => setPassword(e.target.value)}
									required
									placeholder="Min. 8 characters"
									className="input-field pr-10"
									disabled={loading || success}
								/>
								<button
									type="button"
									onClick={() => setShowPassword(!showPassword)}
									className="absolute top-1/2 right-3 -translate-y-1/2 text-zinc-500 transition-colors hover:text-zinc-300"
									aria-label={showPassword ? 'Hide password' : 'Show password'}
								>
									{showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
								</button>
							</div>
						</div>

						{/* Confirm Password */}
						<div className="space-y-2">
							<label
								htmlFor="reg-confirm-password"
								className="text-sm font-medium text-zinc-300"
							>
								Confirm Password
							</label>
							<div className="relative">
								<input
									id="reg-confirm-password"
									type={showConfirmPassword ? 'text' : 'password'}
									value={confirmPassword}
									onChange={(e) => setConfirmPassword(e.target.value)}
									required
									placeholder="Re-enter your password"
									className="input-field pr-10"
									disabled={loading || success}
								/>
								<button
									type="button"
									onClick={() => setShowConfirmPassword(!showConfirmPassword)}
									className="absolute top-1/2 right-3 -translate-y-1/2 text-zinc-500 transition-colors hover:text-zinc-300"
									aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
								>
									{showConfirmPassword ? <EyeOff size={16} /> : <Eye size={16} />}
								</button>
							</div>
							{/* Inline match indicator */}
							{confirmPassword.length > 0 && (
								<p
									className={`text-xs ${
										password === confirmPassword ? 'text-emerald-400' : 'text-red-400'
									}`}
								>
									{password === confirmPassword ? '✓ Passwords match' : '✗ Passwords do not match'}
								</p>
							)}
						</div>

						{/* Role selector */}
						<div className="space-y-2">
							<label className="text-sm font-medium text-zinc-300">Select your role</label>
							<div className="space-y-2">
								{ROLES.map(({ value, label, description, icon: Icon, color, activeColor }) => {
									const isSelected = role === value;
									return (
										<button
											key={value}
											id={`role-${value.toLowerCase()}`}
											type="button"
											onClick={() => setRole(value)}
											disabled={loading || success}
											className={`w-full rounded-xl border px-4 py-3.5 text-left transition-all duration-150 hover:scale-[1.01] active:scale-[0.99] disabled:cursor-not-allowed disabled:opacity-60 ${
												isSelected ? activeColor : `${color} opacity-80`
											}`}
										>
											<div className="flex items-start gap-3">
												<Icon size={18} className="mt-0.5 shrink-0" />
												<div>
													<p className="text-sm font-semibold leading-tight">{label}</p>
													<p className="mt-0.5 text-xs opacity-75">{description}</p>
												</div>
												{isSelected && (
													<CheckCircle2
														size={16}
														className="ml-auto mt-0.5 shrink-0 opacity-90"
													/>
												)}
											</div>
										</button>
									);
								})}
							</div>
						</div>

						{/* Submit */}
						<button
							id="register-submit-btn"
							type="submit"
							disabled={loading || success}
							className="btn-primary w-full py-2.5"
						>
							{loading ? 'Creating account…' : 'Create Account'}
						</button>

						{/* Link back to login */}
						<p className="text-center text-sm text-zinc-500">
							Already have an account?{' '}
							<Link
								to="/login"
								className="font-medium text-zinc-300 underline-offset-4 transition-colors hover:text-white hover:underline"
							>
								Sign in
							</Link>
						</p>
					</form>
				</div>
			</div>
		</div>
	);
}
