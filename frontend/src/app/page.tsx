'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/stores/auth-store';
import { PageLoader } from '@/components/ui/loading';

export default function RootPage() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const { isAuthenticated, isLoading, user } = useAuthStore();

  useEffect(() => setMounted(true), []);

  useEffect(() => {
    if (!mounted || isLoading) return;

    if (!isAuthenticated) {
      router.replace('/login');
      return;
    }

    if (user?.role === 'agent') {
      router.replace('/agent');
    } else {
      router.replace('/admin');
    }
  }, [isAuthenticated, isLoading, mounted, user, router]);

  return <PageLoader message="Redirecting..." />;
}
