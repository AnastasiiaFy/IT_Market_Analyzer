import { Card, CardContent } from "@/components/ui/card";

type Props = {
  data: {
    total?: number;
    remote_percent?: number;
    remote_count?: number;
    office_count?: number;
  };
};

export function RemoteIndexCard({ data }: Props) {
  if (!data) return null;

  return (
    <Card className="w-full h-[450px]">
      <CardContent className="h-full flex flex-col justify-center items-center text-center p-8">

        <h3 className="text-3xl font-semibold">
          Remote-friendly Index
        </h3>

        <p className="text-base text-muted-foreground mt-3">
          Частка вакансій з можливістю віддаленої роботи
        </p>

        <div className="mt-8 text-8xl font-bold text-[#653d6b]">
          {Math.round(data.remote_percent ?? 0)}%
        </div>

        <div className="mt-4 text-lg text-muted-foreground">
          {data.remote_count ?? 0} / {data.total ?? 0} вакансій
        </div>

      </CardContent>
    </Card>
  );
}