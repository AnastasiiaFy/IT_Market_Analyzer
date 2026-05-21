import {
  Card,
  CardContent,
} from "@/components/ui/card";

type Props = {
  data: any;
};

export function SalaryCards({ data }: Props) {
  return (
    <div className="grid md:grid-cols-3 gap-6">
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-muted-foreground text-lg">
            25-й перцентиль
          </p>

          <p className="text-5xl font-bold mt-4">
            ${data.q25}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-muted-foreground text-lg">
            Медіана
          </p>

          <p className="text-5xl font-bold mt-4">
            ${data.median}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-muted-foreground text-lg">
            75-й перцентиль
          </p>

          <p className="text-5xl font-bold mt-4">
            ${data.q75}
          </p>
        </CardContent>
      </Card>
    </div>
  );
}