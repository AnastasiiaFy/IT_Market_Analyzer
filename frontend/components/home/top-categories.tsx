// components/home/top-categories.tsx
import Link from "next/link";
import { Card, CardContent } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

type Category = {
  category: string;
  count: number;
  curr_week: number;
  prev_week: number;
  change: number;
  trend: "up" | "down" | "flat" | string;
};

type Props = {
  categories: Category[];
};

export function TopCategories({ categories }: Props) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      {categories.map((item) => {
        const slug = item.category
          .toLowerCase()
          .replace(/\s+/g, "-");

        const Icon =
          item.trend === "up"
            ? TrendingUp
            : item.trend === "down"
            ? TrendingDown
            : Minus;

        return (
          <Link key={item.category} href={`/dashboard/${slug}`}>
            <Card className="hover:shadow-md transition cursor-pointer">
              <CardContent className="p-4 space-y-2">
                <p className="font-semibold text-lg leading-snug">
                  {item.category}
                </p>

                <p className="text-muted-foreground text-base">
                  {item.curr_week} вакансій
                </p>

                <div className="flex items-center gap-2 text-base">
                  <Icon size={16} />
                  <span>
                    {item.change > 0 ? "+" : ""}
                    {item.change}
                  </span>
                </div>
              </CardContent>
            </Card>
          </Link>
        );
      })}
    </div>
  );
}