"use client";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

type Props = {
  data: any[];
};

function CustomTooltip({
  active,
  payload,
  label,
}: any) {
  if (!active || !payload?.length) {
    return null;
  }

  return (
    <div className="bg-background border rounded-lg p-3 shadow-md">
      <p className="font-semibold">
        {label}
      </p>

      <p>
        Вакансій: {payload[0].value}
      </p>
    </div>
  );
}

export function MonthlyDynamicsChart({
  data,
}: Props) {
  return (
    <div className="border rounded-xl p-4 h-[420px] w-full min-h-[420px]">
      <h3 className="text-xl font-semibold mb-4">
        Помісячна динаміка
      </h3>

      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="4 4" />

          <XAxis dataKey="label" />

          <YAxis />

          <Tooltip
            content={<CustomTooltip />}
          />

          <Line
            type="monotone"
            dataKey="count"
            stroke="#653d6b"
            strokeWidth={4}
            dot={{ r: 5 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}