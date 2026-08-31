import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import MainLayout from './layouts/MainLayout';

import Login from './pages/Login';
import OperatorDashboard from './pages/OperatorDashboard';
import ReviewerDashboard from './pages/ReviewerDashboard';
import ConsumerDashboard from './pages/ConsumerDashboard';
import UploadDataset from './pages/UploadDataset';
import DatasetHistory from './pages/DatasetHistory';
import DatasetDetails from './pages/DatasetDetails';
import ExceptionQueue from './pages/ExceptionQueue';
import VerifiedLoans from './pages/VerifiedLoans';
import AuditTrail from './pages/AuditTrail';

import { useAuth } from './context/AuthContext';

// Routes the user to the correct dashboard based on role
function RoleDashboard() {
	const { user } = useAuth();
	if (!user) return null;
	if (user.role === 'DATA_OPERATOR') return <OperatorDashboard />;
	if (user.role === 'REVIEWER') return <ReviewerDashboard />;
	if (user.role === 'DATA_CONSUMER') return <ConsumerDashboard />;
	return <div className="text-slate-400">Unknown role</div>;
}

export default function App() {
	return (
		<BrowserRouter>
			<AuthProvider>
				<Routes>
					{/* Public */}
					<Route path="/login" element={<Login />} />
					<Route
						path="/"
						element={<Navigate to="/dashboard" replace />}
					/>

					{/* Protected — all authenticated users */}
					<Route
						element={
							<ProtectedRoute>
								<MainLayout />
							</ProtectedRoute>
						}
					>
						<Route path="/dashboard" element={<RoleDashboard />} />

						{/* DATA_OPERATOR routes */}
						<Route
							path="/upload"
							element={
								<ProtectedRoute
									allowedRoles={['DATA_OPERATOR']}
								>
									<UploadDataset />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/datasets"
							element={
								<ProtectedRoute
									allowedRoles={['DATA_OPERATOR']}
								>
									<DatasetHistory />
								</ProtectedRoute>
							}
						/>
						<Route
							path="/datasets/:id"
							element={
								<ProtectedRoute
									allowedRoles={['DATA_OPERATOR']}
								>
									<DatasetDetails />
								</ProtectedRoute>
							}
						/>

						{/* Exception Queue — Reviewer & Operator */}
						<Route
							path="/exceptions"
							element={
								<ProtectedRoute
									allowedRoles={['REVIEWER', 'DATA_OPERATOR']}
								>
									<ExceptionQueue />
								</ProtectedRoute>
							}
						/>

						{/* Verified Loans — Consumer, Reviewer & Operator */}
						<Route
							path="/verified"
							element={
								<ProtectedRoute
									allowedRoles={[
										'DATA_CONSUMER',
										'REVIEWER',
										'DATA_OPERATOR',
									]}
								>
									<VerifiedLoans />
								</ProtectedRoute>
							}
						/>

						{/* Audit Trail — accessible to all authenticated roles */}
						<Route
							path="/audit"
							element={
								<ProtectedRoute>
									<AuditTrail />
								</ProtectedRoute>
							}
						/>
					</Route>

					{/* Fallback */}
					<Route
						path="*"
						element={<Navigate to="/dashboard" replace />}
					/>
				</Routes>
			</AuthProvider>
		</BrowserRouter>
	);
}
