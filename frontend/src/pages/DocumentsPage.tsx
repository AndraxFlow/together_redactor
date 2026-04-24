import { useEffect, useState } from "react"
import { getDocuments, createDocument } from "../api/documents"
import { useNavigate } from "react-router-dom"

export default function DocumentsPage() {
  const [docs, setDocs] = useState<any[]>([])
  const [title, setTitle] = useState("")
  const navigate = useNavigate()

  async function load() {
    try {
      const data = await getDocuments()
      setDocs(data)
    } catch (e) {
      console.error(e)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleCreate() {
    if (!title.trim()) return

    const doc = await createDocument(title)
    setTitle("")
    load()

    // сразу перейти в редактор
    navigate(`/editor/${doc.id}`)
  }

  return (
    <div>
      <h2>Documents</h2>

      <div style={{ marginBottom: 20 }}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Document title"
        />
        <button onClick={handleCreate}>Create</button>
      </div>

      <ul>
        {docs.map((doc) => (
          <li key={doc.id}>
            <button onClick={() => navigate(`/editor/${doc.id}`)}>
              {doc.title}
            </button>
          </li>
        ))}
      </ul>
    </div>
  )
}