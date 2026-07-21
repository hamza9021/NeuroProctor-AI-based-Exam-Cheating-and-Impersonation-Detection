import Sidebar from './Sidebar';
import Navbar from './Navbar';

const Layout = ({ children, title }) => {
  return (
    <div className="min-h-screen bg-neutral-50">
      <Sidebar />
      <div className="lg:ml-64">
        <Navbar title={title} />
        <main className="p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
