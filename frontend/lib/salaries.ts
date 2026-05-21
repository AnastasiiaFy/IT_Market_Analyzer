const API_URL = "http://localhost:8000/api";

export async function getSalaryStats(category: string) {
  const res = await fetch(
    `${API_URL}/salaries?category=${encodeURIComponent(category)}`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch salary stats");
  }

  return res.json();
}