import { SkillCard } from "./skill-level-card";

type Props = {
  skillMap: Record<string, any>;
};

export function SkillsGrid({ skillMap }: Props) {
  const levels = ["Junior", "Middle", "Senior"];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {levels.map((level) => {
        const levelData = skillMap[level];

        if (!levelData) return null;

        return (
          <SkillCard
            key={level}
            level={level}
            data={levelData}
          />
        );
      })}
    </div>
  );
}