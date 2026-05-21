"use client";

import {
  Tabs,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";

type Props = {
  levels: string[];
  value: string;
  onChange: (value: string) => void;
};

export function SalaryTabs({
  levels,
  value,
  onChange,
}: Props) {
  return (
    <Tabs
      value={value}
      onValueChange={onChange}
    >
      <div className="flex justify-end">
        <TabsList
          className="
            h-14
            bg-[#a56dad]
            p-1
          "
        >
          {levels.map((level) => (
            <TabsTrigger
              key={level}
              value={level}
              className="
                px-8
                text-lg
                text-white

                data-[state=active]:bg-white
                data-[state=active]:text-[#653d6b]
              "
            >
              {level}
            </TabsTrigger>
          ))}
        </TabsList>
      </div>
    </Tabs>
  );
}