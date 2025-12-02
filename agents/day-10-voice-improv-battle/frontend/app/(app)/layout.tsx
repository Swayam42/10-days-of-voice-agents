import { headers } from 'next/headers';
import { getAppConfig } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  const hdrs = await headers();
  const { companyName } = await getAppConfig(hdrs);

  return (
    <>
      <header className="fixed top-0 left-0 z-50 w-full flex flex-row justify-center p-6">
        <h1 className="text-xl font-bold tracking-tight">{companyName}</h1>
      </header>

      {children}
    </>
  );
}
