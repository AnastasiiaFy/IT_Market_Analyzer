"use client";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";

type Props = {
  histogram: any[];
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
    <div className="rounded-lg border bg-background p-3 shadow-md">
      <p className="font-medium">
        {label}
      </p>

      <p>
        Анкет: {payload[0].value}
      </p>
    </div>
  );
}

export function SalaryHistogram({
  histogram,
}: Props) {
  return (
    <div className="h-[450px]">
      <ResponsiveContainer
        width="100%"
        height="100%"
      >
        <BarChart data={histogram}>
          <XAxis dataKey="label" />

          <YAxis />

          <Tooltip
            content={<CustomTooltip />}
          />

          <Bar
            dataKey="count"
            fill="#653d6b"
            stroke="#000000"
            strokeWidth={1}
            radius={[8, 8, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}