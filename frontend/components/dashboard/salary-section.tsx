"use client";

import { useState } from "react";

import { SalaryTabs } from "./salary-tabs";
import { SalaryCards } from "./salary-cards";
import { SalaryHistogram } from "./salary-histogram";

type Props = {
  data: any;
};

export function SalarySection({ data }: Props) {
  const levels = Object.keys(data.by_level);

  const [level, setLevel] = useState(levels[0]);

  const current = data.by_level[level];

  return (
    <section className="space-y-8 pt-12">
      <h2 className="text-4xl font-bold text-center">
        Аналітика заробітних плат
      </h2>

      <SalaryTabs
        levels={levels}
        value={level}
        onChange={setLevel}
      />

      <SalaryCards data={current} />

      <SalaryHistogram histogram={current.histogram} />
    </section>
  );
}