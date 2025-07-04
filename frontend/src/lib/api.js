// lib/api.js or similar

// Fetch the latest scanned meal data from the backend
export async function fetchLatestMeal() {
  const response = await fetch(`http://localhost:8000/api/latest-scan/`);

  if (response.status === 204) {
    return null; // No scan yet
  }

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || "Failed to fetch meal data");
  }

  return response.json();
}