import { useEffect, useState } from "react"
import { getDocuments, createDocument } from "../api/documents"
import { useNavigate } from "react-router-dom"

export default function DocumentsPage() {
  const [docs, setDocs] = useState<any[]>([])
  const [title, setTitle] = useState("")
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()

  async function load() {
    try {
      setLoading(true)
      setError(null)
      const data = await getDocuments()
      setDocs(data)
    } catch (e) {
      console.error(e)
      setError("Не удалось загрузить документы")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  async function handleCreate() {
    if (!title.trim()) return

    try {
      const doc = await createDocument(title)
      setTitle("")
      load()
      // сразу перейти в редактор
      navigate(`/editor/${doc.id}`)
    } catch (e) {
      console.error(e)
      setError("Не удалось создать документ")
    }
  }

  return (
    <div>
      <h2>Документы</h2>

      <div style={{ marginBottom: 20 }}>
        <input
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Название документа"
        />
        <button onClick={handleCreate} disabled={!title.trim()}>Создать</button>
      </div>

      {loading && <p>Загрузка...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!loading && !error && docs.length === 0 && <p>У вас нет документов. Создайте первый!</p>}

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