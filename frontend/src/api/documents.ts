const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

function authHeaders() {
  const token = localStorage.getItem("token")

  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  }
}

export async function getDocuments() {
  const res = await fetch(`${API}/documents/`, {
    headers: authHeaders(),
  })

  if (!res.ok) throw new Error("Failed to load documents")

  return res.json()
}

export async function createDocument(title: string) {
  const res = await fetch(`${API}/documents/`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ title }),
  })

  if (!res.ok) throw new Error("Failed to create document")

  return res.json()
}