'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import type { UserRole } from '@/types/models';

interface UseAuthOptions {
  requiredRoles?: UserRole[];
  redirectIfAuthenticated?: boolean;
}

export function useAuth(options?: UseAuthOptions) {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, _hasHydrated, clearAuth } = useAuthStore();

  const requiredRoles = options?.requiredRoles;
  const redirectIfAuthenticated = options?.redirectIfAuthenticated;

  useEffect(() => {
    if (!_hasHydrated || isLoading) return;

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
  }, [isAuthenticated, isLoading, _hasHydrated, user, requiredRoles, redirectIfAuthenticated, router]);

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
