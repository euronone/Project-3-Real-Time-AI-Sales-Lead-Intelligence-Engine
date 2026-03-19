'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { PageLoader } from '@/components/ui/loading';

export default function RootPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, _hasHydrated, user } = useAuthStore();

  useEffect(() => {
    if (!_hasHydrated || isLoading) return;

    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }

    if (user?.role === 'agent') {
      router.replace('/agent');
    } else {
      router.replace('/admin');
    }
  }, [isAuthenticated, isLoading, _hasHydrated, user, router]);

  return <PageLoader message="Redirecting..." />;
}
