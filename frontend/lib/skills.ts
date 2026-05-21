const API_URL = "http://localhost:8000/api";

export async function getSkillMap(category: string) {
  console.log("CATEGORY:", category);

  const url =
    `${API_URL}/skills/map?category=${encodeURIComponent(category)}`;

  console.log("URL:", url);

  const res = await fetch(url);

  if (!res.ok) {
    throw new Error("Failed to fetch skill map");
  }

  return res.json();
}