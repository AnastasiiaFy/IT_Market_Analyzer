import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

type Props = {
  level: string;
  data: any;
};

export function SkillCard({ level, data }: Props) {
  const mustHaveBase = data.must_have.base_stack;

  const mustHaveTitles =
    data.must_have.from_titles.map(
      (skill: any) => skill.skill
    );

  const niceToHaveBase = data.nice_to_have.base_stack;

  const niceToHaveTitles =
    data.nice_to_have.from_titles.map(
      (skill: any) => skill.skill
    );

  return (
    <Card>
      <CardContent className="p-6 space-y-6">
        <h2 className="text-2xl font-bold">
          {level}
        </h2>

        {/* Legend */}
        <div className="flex flex-wrap gap-2">
          <Badge className="px-3 py-1 text-sm">
            Base Stack
          </Badge>

          <Badge
            variant="outline"
            className="
              px-3 py-1 text-sm
              border-[#a56dad]
              text-[#a56dad]
            "
          >
            From Vacancies
          </Badge>
        </div>

        {/* MUST HAVE */}
        <div>
          <h3 className="font-semibold mb-3 text-lg">
            Must Have
          </h3>

          <div className="flex flex-wrap gap-2">
            {mustHaveBase.map((skill: string) => (
              <Badge
                key={`base-${skill}`}
                className="px-3 py-1 text-sm"
              >
                {skill}
              </Badge>
            ))}

            {mustHaveTitles.map((skill: string) => (
              <Badge
                key={`title-${skill}`}
                variant="outline"
                className="
                  px-3 py-1 text-sm
                  border-[#a56dad]
                  text-[#a56dad]
                "
              >
                {skill}
              </Badge>
            ))}
          </div>
        </div>

        {/* NICE TO HAVE */}
        <div>
          <h3 className="font-semibold mb-3 text-lg">
            Nice To Have
          </h3>

          <div className="flex flex-wrap gap-2">
            {niceToHaveBase.map((skill: string) => (
              <Badge
                key={`nice-base-${skill}`}
                variant="secondary"
                className="px-3 py-1 text-sm"
              >
                {skill}
              </Badge>
            ))}

            {niceToHaveTitles.map((skill: string) => (
              <Badge
                key={`nice-title-${skill}`}
                variant="outline"
                className="
                  px-3 py-1 text-sm
                  border-[#a56dad]
                  text-[#a56dad]
                "
              >
                {skill}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}