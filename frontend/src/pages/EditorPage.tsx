import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"

const WS = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws"

export default function EditorPage() {
  const { id } = useParams()
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem("token")

    const ws = new WebSocket(`${WS}/${id}?token=${token}`)

    ws.onopen = () => {
      console.log("WS connected")
      setConnected(true)
    }

    ws.onclose = () => {
      console.log("WS disconnected")
      setConnected(false)
    }

    ws.onerror = (e) => {
      console.error("WS error", e)
    }

    ws.onmessage = (msg) => {
      console.log("WS message received", msg.data)
    }

    return () => {
      ws.close()
    }
  }, [id])

  return (
    <div>
      <h2>Editor #{id}</h2>
      <p>Status: {connected ? "🟢 connected" : "🔴 disconnected"}</p>

      <textarea
        style={{ width: "100%", height: 300 }}
        placeholder="Editor coming next step..."
      />
    </div>
  )
}