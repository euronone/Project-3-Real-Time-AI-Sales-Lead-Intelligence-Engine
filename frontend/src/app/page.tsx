"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/stores/auth-store";
import { PageLoader } from "@/components/ui/loading";

export default function RootPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.replace("/login");
      return;
    }
    if (user?.role === "agent") {
      router.replace("/agent");
    } else {
      router.replace("/admin");
    }
  }, [isAuthenticated, user, router]);

  return <PageLoader message="Loading SalesIQ..." />;
}
