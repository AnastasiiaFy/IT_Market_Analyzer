const API_URL = "http://localhost:8000/api";

export async function getVacancyStats(category: string) {
  const res = await fetch(
    `${API_URL}/vacancies/stats?category=${encodeURIComponent(category)}`,
    {
      cache: "no-store",
    }
  );

  if (!res.ok) {
    throw new Error("Failed to fetch vacancy stats");
  }

  return res.json();
}