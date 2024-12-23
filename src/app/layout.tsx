import './globals.css'
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AllDevs | Desenvolvimento de Software Profissional',
  description: 'Transformamos ideias em soluções digitais inovadoras. Especialistas em desenvolvimento web, mobile e sistemas empresariais.',
  keywords: 'desenvolvimento web, aplicativos mobile, software empresarial, react, node.js, typescript',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="pt-BR" className="scroll-smooth">
      <body className={`${inter.className} antialiased`}>{children}</body>
    </html>
  )
}
