const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

console.log("API_BASE_URL = ", API_BASE_URL);

export async function fetchReceipts() {
  const res = await fetch(`${API_BASE_URL}/receipts`);
  if (!res.ok) throw new Error("Failed to fetch receipts");
  return res.json();
}

export async function uploadReceipt(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/receipts`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Upload failed: ${res.status} - ${text}`);
  }

  return res.json();
}

export async function deleteReceipt(id: number) {
  const res = await fetch(`${API_BASE_URL}/receipts/${id}`, {
    method: "DELETE",
  });

  if (!res.ok) {
    throw new Error("Failed to delete receipt");
  }

  return res.json();
}