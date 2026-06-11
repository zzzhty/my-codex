import { Activity, FileSearch } from "lucide-react";
import { Link, Outlet, useLocation } from "react-router-dom";

export default function Layout() {
  const location = useLocation();

  const navItems = [
    { to: "/audit", label: "Audit", icon: FileSearch },
  ];

  const isActive = (path: string) => location.pathname.startsWith(path);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-950 md:flex">
      <aside className="border-b border-gray-200 bg-white md:fixed md:inset-y-0 md:left-0 md:flex md:w-56 md:flex-col md:border-b-0 md:border-r">
        <div className="flex items-center justify-between gap-3 border-b border-gray-100 p-4">
          <Link to="/audit" className="flex min-w-0 items-center gap-2 text-lg font-semibold text-gray-950">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-emerald-700 text-white">
              <Activity size={17} />
            </span>
            <span className="truncate">DocWatcher</span>
          </Link>
        </div>
        <nav className="flex gap-2 overflow-x-auto p-3 md:flex-1 md:flex-col md:gap-1 md:overflow-visible md:p-4">
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={`flex h-10 items-center gap-3 rounded-md px-3 text-sm transition-colors ${
                isActive(item.to)
                  ? "bg-emerald-50 text-emerald-800 font-medium"
                  : "text-gray-600 hover:bg-gray-100"
              }`}
            >
              <item.icon size={17} />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="hidden border-t border-gray-100 p-4 text-xs text-gray-400 md:block">
          DocWatcher v0.1.0
        </div>
      </aside>
      <main className="min-w-0 flex-1 md:pl-56">
        <div className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
