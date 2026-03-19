'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/stores/auth-store';
import api from '@/lib/api';
import { API_ROUTES } from '@/lib/constants';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Headphones, Mail, Lock, User, Building2, Globe, Eye, EyeOff } from 'lucide-react';

interface RegisterFormData {
  full_name: string;
  email: string;
  password: string;
  confirm_password: string;
  organization_name: string;
  organization_slug: string;
}

interface FormErrors {
  full_name?: string;
  email?: string;
  password?: string;
  confirm_password?: string;
  organization_name?: string;
  organization_slug?: string;
  general?: string;
}

function validateRegisterForm(data: RegisterFormData): FormErrors {
  const errors: FormErrors = {};
  if (!data.full_name.trim()) errors.full_name = 'Full name is required';
  if (!data.email) {
    errors.email = 'Email is required';
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
    errors.email = 'Please enter a valid email';
  }
  if (!data.password) {
    errors.password = 'Password is required';
  } else if (data.password.length < 8) {
    errors.password = 'Password must be at least 8 characters';
  }
  if (data.password !== data.confirm_password) {
    errors.confirm_password = 'Passwords do not match';
  }
  if (!data.organization_name.trim()) errors.organization_name = 'Organization name is required';
  if (!data.organization_slug.trim()) {
    errors.organization_slug = 'Organization slug is required';
  } else if (!/^[a-z0-9-]+$/.test(data.organization_slug)) {
    errors.organization_slug = 'Slug must contain only lowercase letters, numbers, and hyphens';
  }
  return errors;
}

export default function RegisterPage() {
  const router = useRouter();
  const { setAuth, setLoading } = useAuthStore();

  const [formData, setFormData] = useState<RegisterFormData>({
    full_name: '',
    email: '',
    password: '',
    confirm_password: '',
    organization_name: '',
    organization_slug: '',
  });
  const [errors, setErrors] = useState<FormErrors>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));

    // Auto-generate slug from org name
    if (name === 'organization_name') {
      const slug = value
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, '')
        .replace(/\s+/g, '-')
        .replace(/-+/g, '-')
        .trim();
      setFormData((prev) => ({ ...prev, organization_name: value, organization_slug: slug }));
    }

    if (errors[name as keyof FormErrors]) {
      setErrors((prev) => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const validationErrors = validateRegisterForm(formData);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      setLoading(true);

      const { data } = await api.post(API_ROUTES.AUTH.REGISTER, {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        organization_name: formData.organization_name,
        organization_slug: formData.organization_slug,
      });

      const tokenParts = data.access_token.split('.');
      if (tokenParts.length !== 3) throw new Error('Invalid token received');

      const tokenPayload = JSON.parse(atob(tokenParts[1]));

      const user = {
        id: tokenPayload.sub ?? '',
        tenant_id: tokenPayload.tenant_id ?? '',
        email: formData.email,
        full_name: formData.full_name,
        role: tokenPayload.role ?? 'tenant_admin',
        is_active: true,
        last_login: new Date().toISOString(),
        created_at: new Date().toISOString(),
      };

      setAuth(user, data.access_token, data.refresh_token);

      router.push('/admin');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed. Please try again.';
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
            Start Closing More Deals Today
          </h1>
          <p className="text-lg text-blue-100 leading-relaxed">
            Set up your team in minutes. Get AI-powered call intelligence,
            real-time coaching, and deal predictions from day one.
          </p>
          <div className="mt-10 space-y-4">
            {['Real-time call transcription & analysis', 'AI-powered deal prediction', 'Agent coaching & feedback', 'Multi-tenant team management'].map((feature) => (
              <div key={feature} className="flex items-center gap-3">
                <div className="h-5 w-5 rounded-full bg-blue-400/30 flex items-center justify-center">
                  <div className="h-2 w-2 rounded-full bg-white" />
                </div>
                <span className="text-blue-100">{feature}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Right panel — registration form */}
      <div className="flex w-full lg:w-1/2 items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="flex items-center gap-2 mb-8 lg:hidden">
            <Headphones className="h-8 w-8 text-blue-600" />
            <span className="text-2xl font-bold text-gray-900">
              Sales<span className="text-blue-600">IQ</span>
            </span>
          </div>

          <h2 className="text-2xl font-bold text-gray-900 mb-1">Create your account</h2>
          <p className="text-gray-500 mb-8">Get started with a free trial</p>

          {errors.general && (
            <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-700">
              {errors.general}
            </div>
          )}

          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              name="full_name"
              label="Full Name"
              placeholder="John Doe"
              value={formData.full_name}
              onChange={handleChange}
              error={errors.full_name}
              required
              leftIcon={<User size={16} />}
              autoComplete="name"
            />

            <Input
              name="email"
              label="Work Email"
              type="email"
              placeholder="john@company.com"
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
              placeholder="Minimum 8 characters"
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
              autoComplete="new-password"
            />

            <Input
              name="confirm_password"
              label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Re-enter your password"
              value={formData.confirm_password}
              onChange={handleChange}
              error={errors.confirm_password}
              required
              leftIcon={<Lock size={16} />}
              autoComplete="new-password"
            />

            <div className="border-t border-gray-100 my-1" />

            <Input
              name="organization_name"
              label="Organization Name"
              placeholder="Acme Inc."
              value={formData.organization_name}
              onChange={handleChange}
              error={errors.organization_name}
              required
              leftIcon={<Building2 size={16} />}
            />

            <Input
              name="organization_slug"
              label="Organization Slug"
              placeholder="acme-inc"
              value={formData.organization_slug}
              onChange={handleChange}
              error={errors.organization_slug}
              required
              leftIcon={<Globe size={16} />}
              helperText="URL-friendly identifier (auto-generated from org name)"
            />

            <Button
              type="submit"
              isLoading={isSubmitting}
              className="w-full h-11 text-base mt-2"
            >
              Create Account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link
              href="/login"
              className="font-medium text-blue-600 hover:text-blue-700"
            >
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
