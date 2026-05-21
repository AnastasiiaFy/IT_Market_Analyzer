"use client";

import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";

type Props = {
  data: {
    full_time?: { count: number };
    part_time?: { count: number };
    internship?: { count: number };
    temporary?: { count: number };
  };
};

const COLORS = ["#653d6b", "#a56dad", "#d6b7dd", "#8c5d93"];

function CustomTooltip({ active, payload }: any) {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-background border rounded-lg p-3 shadow-md">
      <p className="font-medium">{payload[0].name}</p>
      <p>Вакансій: {payload[0].value}</p>
    </div>
  );
}

export function EmploymentPieChart({ data }: Props) {
  if (!data) return null;

  const chartData = [
    {
      name: "Full-time",
      value: data.full_time?.count ?? 0,
    },
    {
      name: "Part-time",
      value: data.part_time?.count ?? 0,
    },
    {
      name: "Internship",
      value: data.internship?.count ?? 0,
    },
    {
      name: "Temporary",
      value: data.temporary?.count ?? 0,
    },
  ].filter((item) => item.value > 0); // прибираємо нульові сегменти

  return (
    <div className="border rounded-xl p-6 w-full h-[450px] min-h-[450px] relative">
      <h3 className="text-2xl font-semibold mb-4">
        Тип зайнятості
      </h3>

      <div className="w-full h-[380px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius={80}
              outerRadius={140}
              paddingAngle={4}
              cornerRadius={10}
            >
              {chartData.map((_, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index % COLORS.length]}
                  stroke="#000000"
                  strokeWidth={1}
                />
              ))}
            </Pie>

            <Tooltip content={<CustomTooltip />} />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}