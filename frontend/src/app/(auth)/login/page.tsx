'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/auth-store';
import api from '@/lib/api';
import { API_ROUTES } from '@/lib/constants';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Headphones, Mail, Lock, Eye, EyeOff } from 'lucide-react';

interface LoginFormData {
  email: string;
  password: string;
}

interface FormErrors {
  email?: string;
  password?: string;
  general?: string;
}

function validateLoginForm(data: LoginFormData): FormErrors {
  const errors: FormErrors = {};
  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = 'Please enter a valid email address';
  }
  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  }
  return errors;
}

export default function LoginPage() {
  const router = useRouter();
  const { setAuth, setLoading } = useAuthStore();

  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    // Clear field error on change
    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationErrors = validateLoginForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      setLoading(true);

      const { data } = await api.post(API_ROUTES.AUTH.LOGIN, {
        email: formData.email,
        password: formData.password,
      });

      const tokenParts = data.access_token.split('.');
      if (tokenParts.length !== 3) throw new Error('Invalid token received');

      const tokenPayload = JSON.parse(atob(tokenParts[1]));

      const user = {
        id: tokenPayload.sub ?? '',
        tenant_id: tokenPayload.tenant_id ?? '',
        email: formData.email,
        full_name: tokenPayload.full_name ?? formData.email.split('@')[0] ?? 'User',
        role: tokenPayload.role ?? 'agent',
        is_active: true,
        last_login: new Date().toISOString(),
        created_at: tokenPayload.created_at ?? new Date().toISOString(),
      };

      setAuth(user, data.access_token, data.refresh_token);

      if (user.role === 'agent') {
        router.push('/agent');
      } else {
        router.push('/admin');
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed. Please try again.';
      setErrors({ general: message });
      setLoading(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left panel — branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-blue-600 to-blue-800 items-center justify-center p-12">
        <div className="max-w-md text-white">
          <div className="flex items-center gap-3 mb-8">
            <Headphones className="h-10 w-10" />
            <span className="text-3xl font-bold">SalesIQ</span>
          </div>
          <h1 className="text-4xl font-bold mb-4">
            AI-Powered Sales Intelligence
          </h1>
          <p className="text-lg text-blue-100 leading-relaxed">
            Real-time call transcription, AI-guided sales coaching, and
            deal prediction — all in one platform. Close more deals with
            intelligent insights.
          </p>
          <div className="mt-10 grid grid-cols-3 gap-6 text-center">
            <div>
              <p className="text-3xl font-bold">3x</p>
              <p className="text-sm text-blue-200">Faster Deal Closure</p>
            </div>
            <div>
              <p className="text-3xl font-bold">85%</p>
              <p className="text-sm text-blue-200">Prediction Accuracy</p>
            </div>
            <div>
              <p className="text-3xl font-bold">40%</p>
              <p className="text-sm text-blue-200">Revenue Increase</p>
            </div>
          </div>
        </div>
      </div>

      {/* Right panel — login form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <Headphones className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">
              Sales<span className="text-blue-600">IQ</span>
            </span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">Welcome back</h2>
          <p className="text-gray-500 mb-8">Sign in to your account to continue</p>

          {/* General error */}
          {errors.general && (
            <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-5">
            <Input
              name="email"
              label="Email"
              type="email"
              placeholder="you@company.com"
              value={formData.email}
              onChange={handleChange}
              error={errors.email}
              required
              leftIcon={<Mail size={16} />}
              autoComplete="email"
            />

            <Input
              name="password"
              label="Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleChange}
              error={errors.password}
              required
              leftIcon={<Lock size={16} />}
              rightIcon={
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="text-gray-400 hover:text-gray-600"
                  tabIndex={-1}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              }
              autoComplete="current-password"
            />

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 text-sm text-gray-600">
                <input type="checkbox" className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                Remember me
              </label>
              <Link
                href="/forgot-password"
                className="text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                Forgot password?
              </Link>
            </div>

            <Button
              type="submit"
              isLoading={isSubmitting}
              className="w-full h-11 text-base"
            >
              Sign In
            </Button>
          </form>

          <p className="mt-8 text-center text-sm text-gray-500">
            Don&apos;t have an account?{' '}
            <Link
              href="/register"
              className="font-medium text-blue-600 hover:text-blue-700"
            >
              Create an account
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
