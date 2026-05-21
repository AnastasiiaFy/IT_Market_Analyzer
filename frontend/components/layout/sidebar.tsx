"use client";

import Link from "next/link";
import { categoryGroups } from "@/data/categories";
import { useSidebarStore } from "@/store/sidebar-store";
import { X } from "lucide-react";

export function Sidebar() {
  const isOpen = useSidebarStore((s) => s.isOpen);
  const close = useSidebarStore((s) => s.close);
  console.log("sidebar isOpen:", isOpen);

  return (
    <>
      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40"
          onClick={close}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 h-full w-80 bg-background border-r z-50
          transition-transform duration-300
          ${isOpen ? "translate-x-0" : "-translate-x-full"}
        `}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-bold">Категорії</h2>

          <button
            type="button"
            onClick={() => {close()}}
            className="p-2 rounded-md hover:bg-muted"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 space-y-6">
          {categoryGroups.map((group) => (
            <div key={group.title}>
              <h3 className="text-sm uppercase text-muted-foreground mb-2">
                {group.title}
              </h3>

              <div className="flex flex-col space-y-1">
                {group.items.map((item) => (
                  <Link
                    key={item.slug}
                    href={`/dashboard/${item.slug}`}
                    onClick={close}
                    className="block px-3 py-2 rounded-md hover:bg-muted text-sm"
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>
      </aside>
    </>
  );
}