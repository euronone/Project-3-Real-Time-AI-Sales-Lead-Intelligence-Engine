'use client';

import { useState } from 'react';
import Link from 'next/link';
import api from '@/lib/api';
import { API_ROUTES } from '@/lib/constants';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Headphones, Mail, ArrowLeft, CheckCircle } from 'lucide-react';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) {
      setError('Email is required');
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      await api.post(API_ROUTES.AUTH.FORGOT_PASSWORD, { email });
      setIsSuccess(true);
    } catch (err) {
      // Always show success to prevent email enumeration
      setIsSuccess(true);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 p-8">
      <div className="w-full max-w-md">
        <div className="flex items-center gap-2 mb-8">
          <Headphones className="h-8 w-8 text-blue-600" />
          <span className="text-2xl font-bold text-gray-900">
            Sales<span className="text-blue-600">IQ</span>
          </span>
        </div>

        {isSuccess ? (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-green-100">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Check your email</h2>
            <p className="text-gray-500 mb-8">
              If an account exists with <strong>{email}</strong>, we&apos;ve sent password reset instructions.
            </p>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
            >
              <ArrowLeft size={16} />
              Back to sign in
            </Link>
          </div>
        ) : (
          <>
            <h2 className="text-2xl font-bold text-gray-900 mb-1">Forgot password?</h2>
            <p className="text-gray-500 mb-8">
              Enter your email and we&apos;ll send you instructions to reset your password.
            </p>

            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              <Input
                name="email"
                label="Email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (error) setError('');
                }}
                error={error}
                required
                leftIcon={<Mail size={16} />}
                autoComplete="email"
              />

              <Button type="submit" isLoading={isSubmitting} className="w-full h-11 text-base">
                Send Reset Instructions
              </Button>
            </form>

            <p className="mt-6 text-center">
              <Link
                href="/login"
                className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:text-blue-700"
              >
                <ArrowLeft size={16} />
                Back to sign in
              </Link>
            </p>
          </>
        )}
      </div>
    </div>
  );
}
