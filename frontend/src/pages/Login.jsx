import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
	ShieldCheck,
	Eye,
	EyeOff,
	AlertCircle,
	CheckCircle2,
} from 'lucide-react';

const DEMO_CREDS = [
	{
		role: 'Data Operator',
		email: 'operator@test.com',
		password: 'password123',
		color: 'bg-blue-950/40 border-blue-800/40 text-blue-300',
	},
	{
		role: 'Reviewer',
		email: 'reviewer@test.com',
		password: 'password123',
		color: 'bg-amber-950/40 border-amber-800/40 text-amber-300',
	},
	{
		role: 'Data Consumer',
		email: 'consumer@test.com',
		password: 'password123',
		color: 'bg-emerald-950/40 border-emerald-800/40 text-emerald-300',
	},
];

export default function Login() {
	const [email, setEmail] = useState('');
	const [password, setPassword] = useState('');
	const [showPassword, setShowPassword] = useState(false);
	const [error, setError] = useState('');
	const [loading, setLoading] = useState(false);

	const { login } = useAuth();
	const navigate = useNavigate();

	const handleSubmit = async (e) => {
		e.preventDefault();
		setError('');
		setLoading(true);
		try {
			await login(email, password);
			navigate('/dashboard');
		} catch (err) {
			setError(err.response?.data?.detail || 'Invalid email or password');
		} finally {
			setLoading(false);
		}
	};

	const fillCredentials = (creds) => {
		setEmail(creds.email);
		setPassword(creds.password);
		setError('');
	};

	return (
		<div className="flex min-h-screen bg-black text-zinc-200">
			{/* Left panel — branding */}
			<div className="hidden flex-col justify-between border-r border-zinc-800/80 bg-zinc-950 p-12 lg:flex lg:w-1/2">
				<div className="flex items-center gap-3">
					<div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white shadow-sm">
						<ShieldCheck size={22} className="text-black" />
					</div>
					<div>
						<p className="text-lg leading-tight font-bold tracking-tight text-white">
							Loan Copilot
						</p>
						<p className="text-sm text-zinc-500">
							Data Verification Platform
						</p>
					</div>
				</div>

				<div className="max-w-lg space-y-6">
					<div>
						<h2 className="text-4xl leading-tight font-extrabold tracking-tight text-white">
							Trusted Loan Data.
							<br />
							<span className="font-light text-zinc-400">
								Validated & Verified.
							</span>
						</h2>
						<p className="mt-4 text-sm leading-relaxed text-zinc-400">
							Ingest messy financial tapes, normalize them into a
							canonical internal schema, run multi-rule
							validation, resolve exceptions with AI assistance,
							and maintain an immutable audit trail.
						</p>
					</div>

					<div className="space-y-3 pt-2">
						{[
							'Preserves immutable raw records in JSONB',
							'15-rule automated financial validation engine',
							'AI copilot for smart exception resolution',
							'Cryptographic SHA-256 verified record hashes',
						].map((f) => (
							<div
								key={f}
								className="flex items-center gap-2.5 text-sm text-zinc-300"
							>
								<CheckCircle2
									size={16}
									className="shrink-0 text-white"
								/>
								<span>{f}</span>
							</div>
						))}
					</div>
				</div>

				<p className="font-mono text-xs text-zinc-600">
					Intain Campus FinTech Challenge 2026
				</p>
			</div>

			{/* Right panel — login form */}
			<div className="flex flex-1 items-center justify-center bg-black p-8">
				<div className="w-full max-w-md space-y-8">
					<div>
						<h1 className="text-2xl font-bold tracking-tight text-white">
							Sign in to your account
						</h1>
						<p className="mt-1 text-sm text-zinc-400">
							Enter your credentials to continue to the platform
						</p>
					</div>

					{error && (
						<div className="flex items-center gap-2 rounded-lg border border-red-800/80 bg-red-950/60 px-4 py-3 text-sm text-red-300">
							<AlertCircle size={16} />
							<span>{error}</span>
						</div>
					)}

					<form
						id="login-form"
						onSubmit={handleSubmit}
						className="space-y-5"
					>
						<div className="space-y-2">
							<label
								htmlFor="email"
								className="text-sm font-medium text-zinc-300"
							>
								Email Address
							</label>
							<input
								id="email"
								type="email"
								value={email}
								onChange={(e) => setEmail(e.target.value)}
								required
								placeholder="operator@test.com"
								className="input-field"
							/>
						</div>

						<div className="space-y-2">
							<label
								htmlFor="password"
								className="text-sm font-medium text-zinc-300"
							>
								Password
							</label>
							<div className="relative">
								<input
									id="password"
									type={showPassword ? 'text' : 'password'}
									value={password}
									onChange={(e) =>
										setPassword(e.target.value)
									}
									required
									placeholder="••••••••"
									className="input-field pr-10"
								/>
								<button
									type="button"
									onClick={() =>
										setShowPassword(!showPassword)
									}
									className="absolute top-1/2 right-3 -translate-y-1/2 text-zinc-500 transition-colors hover:text-zinc-300"
								>
									{showPassword ? (
										<EyeOff size={16} />
									) : (
										<Eye size={16} />
									)}
								</button>
							</div>
						</div>

						<button
							id="login-submit-btn"
							type="submit"
							disabled={loading}
							className="btn-primary w-full py-2.5"
						>
							{loading ? 'Signing in...' : 'Sign In'}
						</button>
					</form>

					{/* Demo Credentials Helper */}
					<div className="border-t border-zinc-800/80 pt-6">
						<p className="mb-3 text-xs font-semibold tracking-wider text-zinc-500 uppercase">
							Quick-Fill Test Credentials
						</p>
						<div className="space-y-2">
							{DEMO_CREDS.map((cred) => (
								<button
									key={cred.role}
									type="button"
									onClick={() => fillCredentials(cred)}
									className={`w-full rounded-lg border px-3.5 py-2.5 text-left text-xs transition-all hover:scale-[1.01] active:scale-[0.99] ${cred.color}`}
								>
									<span className="font-semibold">
										{cred.role}
									</span>
									<span className="ml-2 font-mono opacity-70">
										{cred.email}
									</span>
								</button>
							))}
						</div>
						<p className="mt-2 text-xs text-zinc-600">
							Click any role to autofill test credentials.
						</p>
					</div>
				</div>
			</div>
		</div>
	);
}
