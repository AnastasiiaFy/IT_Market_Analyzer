// components/home/hero.tsx
import Image from "next/image";
import { getSummary } from "@/lib/api";
import { StatsCard } from "./stats-card";
import { TopCategories } from "./top-categories";

import { Separator } from "@/components/ui/separator";

export default async function Hero() {
  const data = await getSummary();

  return (
    <section className="container mx-auto pt-[70px] pb-12 space-y-10">
      {/* 1. Заголовок */}
      <div className="max-w-3xl">
        <h1 className="text-5xl font-bold leading-tight">
          Ukraine IT Market Analytics 
        </h1>

        <p className="mt-4 text-lg text-muted-foreground">
          Аналітика IT-вакансій в Україні на основі щотижневого збору даних:
          попит, зарплати, навички та тренди ринку.
        </p>
      </div>

      {/* 2. Фото */}
      <div className="relative w-full h-[340px] rounded-xl overflow-hidden">
        <Image
          src="/hero.svg"
          alt="IT analytics dashboard"
          width={1600}
          height={250}
          className="object-cover"
          priority
        />
      </div>

      <div className="space-y-3">
        <h2 className="text-2xl font-semibold">
          Досліджено
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <StatsCard
            title="категорій"
            value={data.total_categories}
            open_sidebar={true}
          />

          <StatsCard
            title="вакансій"
            value={data.total_vacancies}
            open_sidebar={false}
          />
        </div>
    </div>

      <Separator className="my-5 opacity-100" />

      {/* 4. Топ-5 категорій */}
      <div>
        <h2 className="text-2xl font-semibold mb-4">
          Кількість нових вакансій на топ-5 спеціалізацій за останній тиждень
        </h2>

        <TopCategories categories={data.top_categories} />
      </div>
    </section>
  );
}