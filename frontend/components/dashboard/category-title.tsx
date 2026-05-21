type Props = {
  title: string;
};

export function CategoryTitle({ title }: Props) {
  return (
    <div className="text-center">
      <h1 className="text-5xl font-bold">
        {title}
      </h1>
    </div>
  );
}