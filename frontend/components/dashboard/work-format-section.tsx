import { EmploymentPieChart } from "./employment-pie-chart";
import { RemoteIndexCard } from "./remote-index-card";

type Props = {
  employment: Record<string, any>;
  remote: Record<string, any>;
  category: string;
};

export function WorkFormatSection({
  employment,
  remote,
}: Props) {
  const employmentData = employment;
  const remoteData = remote;

  if (!employmentData || !remoteData) {
    return null;
  }

  return (
    <section className="space-y-10 pt-16">

      <h2 className="text-4xl font-bold text-center">
        Формат роботи
      </h2>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 items-stretch">

        <div className="xl:col-span-2">
          <EmploymentPieChart data={employmentData} />
        </div>

        <div>
          <RemoteIndexCard data={remoteData} />
        </div>

      </div>

    </section>
  );
}