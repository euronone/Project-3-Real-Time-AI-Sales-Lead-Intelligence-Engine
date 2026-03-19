'use client';

import { useAuthStore } from '@/stores/auth-store';
import { Bell } from 'lucide-react';
import { Avatar } from '@/components/ui/avatar';

export function Header() {
  const { user } = useAuthStore();

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-gray-200 bg-white/80 backdrop-blur-sm px-6">
      {/* Left: page context placeholder */}
      <div />

      {/* Right: notifications + user */}
      <div className="flex items-center gap-4">
        {/* Notification bell */}
        <button
          className="relative rounded-lg p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors"
          title="Notifications"
        >
          <Bell size={20} />
          {/* Unread dot — will be wired to notification store later */}
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-red-500" />
        </button>

        {/* User avatar */}
        <div className="flex items-center gap-2">
          <Avatar
            name={user?.full_name ?? 'User'}
            size="sm"
          />
          <div className="hidden sm:block">
            <p className="text-sm font-medium text-gray-900">{user?.full_name ?? 'User'}</p>
            <p className="text-xs text-gray-500 capitalize">{user?.role?.replace('_', ' ') ?? 'Agent'}</p>
          </div>
        </div>
      </div>
    </header>
  );
}
