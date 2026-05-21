const API_URL = "http://localhost:8000/api";

export async function getSummary() {
  const response = await fetch(
    `${API_URL}/summary`,
    {
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch summary");
  }

  return response.json();
}


