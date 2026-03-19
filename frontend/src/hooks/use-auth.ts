'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import type { UserRole } from '@/types/models';

interface UseAuthOptions {
  requiredRoles?: UserRole[];
  redirectIfAuthenticated?: boolean;
}

export function useAuth(options?: UseAuthOptions) {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const { user, isAuthenticated, isLoading, clearAuth } = useAuthStore();

  const requiredRoles = options?.requiredRoles;
  const redirectIfAuthenticated = options?.redirectIfAuthenticated;

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!mounted || isLoading) return;

    if (redirectIfAuthenticated && isAuthenticated) {
      router.replace(user?.role === 'agent' ? '/agent' : '/admin');
      return;
    }

    if (!isAuthenticated && !redirectIfAuthenticated) {
      router.replace('/login');
      return;
    }

    if (requiredRoles && user && !requiredRoles.includes(user.role)) {
      router.replace(user.role === 'agent' ? '/agent' : '/admin');
    }
  }, [isAuthenticated, isLoading, mounted, user, requiredRoles, redirectIfAuthenticated, router]);

  const logout = () => {
    clearAuth();
    router.replace('/login');
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    logout,
    isAdmin: user?.role === 'tenant_admin' || user?.role === 'super_admin',
    isManager: user?.role === 'manager',
    isAgent: user?.role === 'agent',
  };
}
