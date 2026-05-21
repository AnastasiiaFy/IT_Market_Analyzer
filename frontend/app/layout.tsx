//'use client'; // 1. Обов'язково додаємо цю директиву в самий верх


import "./globals.css";
import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Sidebar />
        <Header />
        {children}
      </body>
    </html>
  );
}