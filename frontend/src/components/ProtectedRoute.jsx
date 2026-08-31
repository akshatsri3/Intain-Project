import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * Wraps a route and redirects to /login if the user is not authenticated.
 * Optionally restricts to specific roles.
 */
export default function ProtectedRoute({ children, allowedRoles }) {
	const { user, loading } = useAuth();

	if (loading) {
		return (
			<div className="flex min-h-screen items-center justify-center bg-slate-950">
				<div className="text-sm text-slate-400">Loading...</div>
			</div>
		);
	}

	if (!user) {
		return <Navigate to="/login" replace />;
	}

	if (allowedRoles && !allowedRoles.includes(user.role)) {
		return <Navigate to="/dashboard" replace />;
	}

	return children;
}
