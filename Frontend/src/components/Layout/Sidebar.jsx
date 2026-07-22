import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  FileText,
  Shield,
  Settings, 
  LogOut, 
  Menu, 
  X,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);
  const location = useLocation();
  const { user, logout } = useAuth();

  const navigation = [
    { name: 'Dashboard', href: user?.role === 'admin' ? '/admin/dashboard' : '/invigilator/dashboard', icon: LayoutDashboard },
    { name: 'Admin Management', href: '/admin', icon: Shield, adminOnly: true },
    { name: 'Students', href: '/students', icon: Users },
    { name: 'Exams', href: '/exams', icon: FileText },
    { name: 'Settings', href: '/settings', icon: Settings },
  ].filter(item => {
    // Hide Students and Exams for admin
    if (user?.role === 'admin' && (item.name === 'Students' || item.name === 'Exams')) {
      return false;
    }
    // Hide admin-only items for non-admin users
    if (item.adminOnly && user?.role !== 'admin') {
      return false;
    }
    return true;
  });

  const isActive = (href) => location.pathname === href;

  const handleLogout = () => {
    logout();
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-screen bg-white border-r border-neutral-200
          transition-all duration-300 ease-in-out
          ${isCollapsed ? 'w-20' : 'w-64'}
          ${isMobileOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
      >
        {/* Logo */}
        <div className="flex items-center justify-between h-16 px-4 border-b border-neutral-200">
          {!isCollapsed && (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 flex items-center justify-center">
                <img src="/src/Assets/Logo.png" alt="NeuroProctor" className="w-full h-full object-contain" />
              </div>
              <span className="font-semibold text-neutral-900">NeuroProctor</span>
            </div>
          )}
          {isCollapsed && (
            <div className="w-8 h-8 flex items-center justify-center mx-auto">
              <img src="/src/Assets/Logo.png" alt="NeuroProctor" className="w-full h-full object-contain" />
            </div>
          )}
          <button
            onClick={() => setIsMobileOpen(false)}
            className="lg:hidden p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`
                flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200
                ${isActive(item.href)
                  ? 'bg-accent/10 text-accent'
                  : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
                }
              `}
              title={isCollapsed ? item.name : ''}
            >
              <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive(item.href) ? 'text-accent' : ''}`} />
              {!isCollapsed && (
                <span className="font-medium text-sm">{item.name}</span>
              )}
              {isActive(item.href) && !isCollapsed && (
                <div className="ml-auto w-1.5 h-1.5 bg-accent rounded-full" />
              )}
            </Link>
          ))}
        </nav>

        {/* Collapse toggle */}
        <div className="absolute bottom-20 left-0 right-0 px-4 hidden lg:block">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="w-full flex items-center justify-center p-2 text-neutral-400 hover:text-neutral-600 hover:bg-neutral-100 rounded-lg transition-colors"
          >
            {isCollapsed ? (
              <ChevronRight className="w-5 h-5" />
            ) : (
              <ChevronLeft className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Logout */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-neutral-200">
          <button
            onClick={handleLogout}
            className={`
              flex items-center gap-3 w-full px-3 py-2.5 rounded-lg transition-all duration-200
              ${isCollapsed ? 'justify-center' : ''}
              text-neutral-600 hover:bg-red-50 hover:text-red-600
            `}
            title={isCollapsed ? 'Logout' : ''}
          >
            <LogOut className="w-5 h-5 flex-shrink-0" />
            {!isCollapsed && (
              <span className="font-medium text-sm">Logout</span>
            )}
          </button>
        </div>
      </aside>

      {/* Mobile menu button */}
      <button
        onClick={() => setIsMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-30 p-2 bg-white border border-neutral-200 rounded-lg shadow-sm"
      >
        <Menu className="w-5 h-5" />
      </button>
    </>
  );
};

export default Sidebar;
