"use client";

import { ArrowBigRightDash } from "lucide-react";
import { useSidebarStore } from "@/store/sidebar-store";

export function Header() {
  const open = useSidebarStore((s) => s.open);
  const isOpen = useSidebarStore((s) => s.isOpen);

  if (isOpen) return null;

  return (
    <div className="fixed top-10 left-4 z-50">
      <button
        onClick={open}
        className="p-2 rounded-md hover:bg-muted transition bg-background border shadow-sm"
      >
        <ArrowBigRightDash className="w-5 h-5" />
      </button>
    </div>
  );
}