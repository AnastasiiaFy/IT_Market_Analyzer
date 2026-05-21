// components/home/stats-card.tsx
"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

import { ArrowUpRight } from "lucide-react";
import { useSidebarStore } from "@/store/sidebar-store";

type Props = {
  title: string;
  value: number;
  open_sidebar?: boolean;
};

export function StatsCard({ title, value, open_sidebar }: Props) {
    const open = useSidebarStore((state) => state.open);
    const showIconButton = open_sidebar === true;

    return (
        <Card className="p-6 flex items-center justify-between">
        <CardContent className="p-0 flex items-center justify-between w-full">

            <div className="flex items-center gap-4">
                <p className="text-5xl font-bold">{value}</p>
                <p className="text-3xl text-muted-foreground">{title}</p>
            </div>

            {showIconButton && (
            <Button variant="secondary" className="w-12 h-12" onClick={open}>
                <ArrowUpRight className="w-6 h-6" />
            </Button>
            )}
        </CardContent>
        </Card>
    );
}
