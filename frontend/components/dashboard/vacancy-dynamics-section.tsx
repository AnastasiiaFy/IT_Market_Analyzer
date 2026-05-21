import { MonthlyDynamicsChart } from "./monthly-dynamics-chart";
import { WeeklyDynamicsChart } from "./weekly-dynamics-chart";

type Props = {
  data: {
    monthly: any[];
    weekly: any[];
  };
};

export function VacancyDynamicsSection({
  data,
}: Props) {
  return (
    <section className="space-y-10 pt-12">

      <h2 className="text-4xl font-bold text-center">
        Аналітика кількості вакансій
      </h2>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">

        <div className="xl:col-span-2">
          <MonthlyDynamicsChart
            data={data.monthly}
          />
        </div>

        <div>
          <WeeklyDynamicsChart
            data={data.weekly}
          />
        </div>

      </div>
    </section>
  );
}