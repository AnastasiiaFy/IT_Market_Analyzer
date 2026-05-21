import { notFound } from "next/navigation";

import { findCategoryBySlug } from "@/data/categories";
import { getSkillMap } from "@/lib/skills";

import { CategoryTitle } from "@/components/dashboard/category-title";
import { SkillsGrid } from "@/components/dashboard/skills-grid";

import { getSalaryStats } from "@/lib/salaries";
import { SalarySection } from "@/components/dashboard/salary-section";

import { getVacancyStats } from "@/lib/vacancies";
import { VacancyDynamicsSection } from "@/components/dashboard/vacancy-dynamics-section";

import { WorkFormatSection } from "@/components/dashboard/work-format-section";

type Props = {
  params: Promise<{
    slug: string;
  }>;
};

export default async function CategoryPage({ params }: Props) {
  const { slug } = await params;

  const category = findCategoryBySlug(slug);

  if (!category) {
    notFound();
  }

  const data = await getSkillMap(category.label);

  const salaryData = await getSalaryStats(category.label);

  const vacancyStats = await getVacancyStats(category.label);

  return (
    <main className="container mx-auto py-12 space-y-10">

      <CategoryTitle
        title={data.category}
      />

      <h2 className="text-4xl font-bold text-center">
        Skill Map
      </h2>

      <SkillsGrid
        skillMap={data.skill_map}
      />

      <SalarySection data={salaryData} />

      <VacancyDynamicsSection
        data={vacancyStats.vacancy_dynamics}
      />

      <WorkFormatSection
        employment={vacancyStats.employment_type}
        remote={vacancyStats.remote_index}
        category={category.label}
      />

    </main>
  );
}

