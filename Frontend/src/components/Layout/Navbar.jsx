import { Search, Bell, User } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Navbar = ({ title }) => {
  const { user } = useAuth();

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-neutral-200">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Page title */}
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900">{title}</h1>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative hidden md:block">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Search..."
              className="pl-10 pr-4 py-2 w-64 border border-neutral-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-accent focus:border-transparent"
            />
          </div>

          {/* Notifications */}
          <button className="relative p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors">
            <Bell className="w-5 h-5" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
          </button>

          {/* User profile */}
          <div className="flex items-center gap-3 pl-4 border-l border-neutral-200">
            <div className="text-right hidden sm:block">
              <p className="text-sm font-medium text-neutral-900">
                {user?.fullName || 'User'}
              </p>
              <p className="text-xs text-neutral-500 capitalize">
                {user?.role || 'Invigilator'}
              </p>
            </div>
            <div className="w-10 h-10 rounded-full overflow-hidden bg-neutral-200">
              <img src={user.profileImage} alt="" className="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
