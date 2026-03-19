'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Home } from 'lucide-react';

interface BreadcrumbItem {
  label: string;
  href?: string;
}

function pathToBreadcrumbs(pathname: string): BreadcrumbItem[] {
  const segments = pathname.split('/').filter(Boolean);
  const crumbs: BreadcrumbItem[] = [];

  // Map known segments to human-readable labels
  const labelMap: Record<string, string> = {
    admin: 'Admin',
    agent: 'Agent',
    agents: 'Agents',
    leads: 'Leads',
    calls: 'Calls',
    campaigns: 'Campaigns',
    analytics: 'Analytics',
    settings: 'Settings',
    predictions: 'Deal Pipeline',
    coaching: 'AI Coaching',
    'lead-flows': 'Lead Flows',
    'call-routing': 'Call Routing',
    'audit-log': 'Audit Log',
    'active-call': 'Active Call',
    'forgot-password': 'Forgot Password',
  };

  let currentPath = '';
  for (let i = 0; i < segments.length; i++) {
    const segment = segments[i]!;
    currentPath += `/${segment}`;

    // Skip dynamic route [id] segments — replace with "Detail"
    if (segment.startsWith('[') || /^[0-9a-f-]{36}$/i.test(segment)) {
      crumbs.push({ label: 'Detail' });
      continue;
    }

    const label = labelMap[segment] ?? segment.charAt(0).toUpperCase() + segment.slice(1);
    const isLast = i === segments.length - 1;

    crumbs.push({
      label,
      href: isLast ? undefined : currentPath,
    });
  }

  return crumbs;
}

export function Breadcrumb() {
  const pathname = usePathname();
  const crumbs = pathToBreadcrumbs(pathname);

  if (crumbs.length <= 1) return null;

  return (
    <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm text-gray-500 mb-4">
      <Link href="/" className="hover:text-gray-700 transition-colors">
        <Home size={14} />
      </Link>
      {crumbs.map((crumb, idx) => (
        <span key={idx} className="flex items-center gap-1.5">
          <ChevronRight size={14} className="text-gray-300" />
          {crumb.href ? (
            <Link href={crumb.href} className="hover:text-gray-700 transition-colors">
              {crumb.label}
            </Link>
          ) : (
            <span className="text-gray-900 font-medium">{crumb.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
