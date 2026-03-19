'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { useAuthStore } from '@/stores/auth-store';
import type { UserRole } from '@/types/models';
import {
  LayoutDashboard,
  Users,
  Contact,
  Phone,
  BarChart3,
  Settings,
  FileText,
  Route,
  Megaphone,
  Shield,
  Brain,
  TrendingUp,
  Headphones,
  LogOut,
} from 'lucide-react';

interface NavItem {
  href: string;
  label: string;
  icon: React.ReactNode;
  roles: UserRole[];
}

const NAV_ITEMS: NavItem[] = [
  // Admin items
  { href: '/admin', label: 'Dashboard', icon: <LayoutDashboard size={20} />, roles: ['super_admin', 'tenant_admin', 'manager'] },
  { href: '/admin/agents', label: 'Agents', icon: <Users size={20} />, roles: ['super_admin', 'tenant_admin', 'manager'] },
  { href: '/admin/leads', label: 'Leads', icon: <Contact size={20} />, roles: ['super_admin', 'tenant_admin', 'manager'] },
  { href: '/admin/campaigns', label: 'Campaigns', icon: <Megaphone size={20} />, roles: ['super_admin', 'tenant_admin', 'manager'] },
  { href: '/admin/lead-flows', label: 'Lead Flows', icon: <Route size={20} />, roles: ['super_admin', 'tenant_admin'] },
  { href: '/admin/call-routing', label: 'Call Routing', icon: <Phone size={20} />, roles: ['super_admin', 'tenant_admin'] },
  { href: '/admin/analytics', label: 'Analytics', icon: <BarChart3 size={20} />, roles: ['super_admin', 'tenant_admin', 'manager'] },
  { href: '/admin/audit-log', label: 'Audit Log', icon: <Shield size={20} />, roles: ['super_admin', 'tenant_admin'] },
  { href: '/admin/settings', label: 'Settings', icon: <Settings size={20} />, roles: ['super_admin', 'tenant_admin'] },
  // Agent items
  { href: '/agent', label: 'Dashboard', icon: <LayoutDashboard size={20} />, roles: ['agent'] },
  { href: '/agent/calls', label: 'Calls', icon: <Phone size={20} />, roles: ['agent'] },
  { href: '/agent/leads', label: 'My Leads', icon: <Contact size={20} />, roles: ['agent'] },
  { href: '/agent/predictions', label: 'Deal Pipeline', icon: <TrendingUp size={20} />, roles: ['agent'] },
  { href: '/agent/coaching', label: 'AI Coaching', icon: <Brain size={20} />, roles: ['agent'] },
];

export function Sidebar() {
  const pathname = usePathname();
  const { user, clearAuth } = useAuthStore();
  const role = user?.role ?? 'agent';

  const filteredItems = NAV_ITEMS.filter((item) => item.roles.includes(role));

  return (
    <aside className="fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-gray-200 bg-white">
      {/* Logo */}
      <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6">
        <Headphones className="h-7 w-7 text-blue-600" />
        <span className="text-xl font-bold text-gray-900">
          Sales<span className="text-blue-600">IQ</span>
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="flex flex-col gap-1">
          {filteredItems.map((item) => {
            const isActive =
              pathname === item.href ||
              (item.href !== '/admin' && item.href !== '/agent' && pathname.startsWith(item.href));

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-blue-50 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <span className={cn(isActive ? 'text-blue-600' : 'text-gray-400')}>
                    {item.icon}
                  </span>
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* User + Logout */}
      <div className="border-t border-gray-200 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700">
            {user?.full_name
              ?.split(' ')
              .map((n) => n[0])
              .join('')
              .toUpperCase()
              .slice(0, 2) ?? '??'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="truncate text-sm font-medium text-gray-900">{user?.full_name ?? 'User'}</p>
            <p className="truncate text-xs text-gray-500">{user?.email ?? ''}</p>
          </div>
          <button
            onClick={() => {
              clearAuth();
              window.location.href = '/login';
            }}
            className="rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
            title="Log out"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>
    </aside>
  );
}
