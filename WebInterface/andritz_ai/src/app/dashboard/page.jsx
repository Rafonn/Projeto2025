'use client';

import { useEffect } from 'react';
import { useSession, signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.replace('/login');
    }
  }, [status, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-white text-lg">Carregando...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center">
      <h1 className="text-3xl font-bold mb-4">Bem-vindo, {session?.user?.email}!</h1>
      <p className="mb-6">Este é o seu dashboard protegido.</p>
      <button
        onClick={async () => {
          await signOut({ redirect: false });
          router.replace('/login');
        }}
        className="px-6 py-2 bg-red-600 rounded hover:bg-red-700 transition"
      >
        Sair
      </button>
    </div>
  );
}
