import {
	createContext,
	useContext,
	useState,
	useEffect,
	useCallback,
} from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
	const [user, setUser] = useState(null);
	const [loading, setLoading] = useState(true);

	// On mount, try to restore session from stored token
	useEffect(() => {
		const token = localStorage.getItem('token');
		if (token) {
			authService
				.getMe()
				.then(setUser)
				.catch(() => {
					localStorage.removeItem('token');
					setUser(null);
				})
				.finally(() => setLoading(false));
		} else {
			setLoading(false);
		}
	}, []);

	const login = useCallback(async (email, password) => {
		const { access_token } = await authService.login(email, password);
		localStorage.setItem('token', access_token);
		const me = await authService.getMe();
		setUser(me);
		return me;
	}, []);

	const logout = useCallback(() => {
		localStorage.removeItem('token');
		setUser(null);
	}, []);

	return (
		<AuthContext.Provider value={{ user, loading, login, logout }}>
			{children}
		</AuthContext.Provider>
	);
}

export function useAuth() {
	const ctx = useContext(AuthContext);
	if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
	return ctx;
}
