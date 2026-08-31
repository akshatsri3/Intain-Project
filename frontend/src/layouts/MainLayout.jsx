import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import Header from '../components/Header';

export default function MainLayout({ title }) {
	return (
		<div className="flex min-h-screen bg-black">
			<Sidebar />
			<div className="flex min-w-0 flex-1 flex-col">
				<Header title={title} />
				<main className="flex-1 overflow-auto p-6">
					<Outlet />
				</main>
			</div>
		</div>
	);
}
