'use client';

import { useAuth } from '@/hooks/use-auth';

export default function AgentDashboardPage() {
  const { user } = useAuth({
    requiredRoles: ['agent'],
  });

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-1">
        Welcome, {user?.full_name?.split(' ')[0] ?? 'Agent'}
      </h1>
      <p className="text-gray-500 mb-8">
        Here&apos;s your daily overview. Start making calls to hit your targets.
      </p>

      {/* Agent KPI cards — placeholder */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {[
          { label: 'Calls Today', value: '—' },
          { label: 'Leads Assigned', value: '—' },
          { label: 'Win Rate', value: '—' },
          { label: 'Avg. AI Score', value: '—' },
        ].map((kpi) => (
          <div
            key={kpi.label}
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
          >
            <p className="text-sm text-gray-500 mb-2">{kpi.label}</p>
            <p className="text-3xl font-bold text-gray-900">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Placeholder sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm h-64 flex items-center justify-center">
          <p className="text-gray-400 text-sm">Call Queue — Coming in Day 2</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm h-64 flex items-center justify-center">
          <p className="text-gray-400 text-sm">AI Coaching Feedback — Coming in Day 2</p>
        </div>
      </div>
    </div>
  );
}
