import { useParams } from "react-router-dom"
import { useEffect, useRef, useState } from "react"
import { getToken } from "../lib/storage"
import * as Y from "yjs"
import { ShareForm } from "../components/ShareForm"

const WS = import.meta.env.VITE_WS_URL || "ws://localhost:8000/ws"

export default function EditorPage() {
  const { id } = useParams()
  const [connected, setConnected] = useState(false)
  const [showShare, setShowShare] = useState(false)

  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  const ydocRef = useRef<Y.Doc | null>(null)
  const ytextRef = useRef<Y.Text | null>(null)
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const token = getToken()
    if (!token || !id) return

    console.log("🔑 TOKEN:", token)

    // --- YJS INIT ---
    const ydoc = new Y.Doc()
    const ytext = ydoc.getText("content")

    ydocRef.current = ydoc
    ytextRef.current = ytext

    // --- WS ---
    const ws = new WebSocket(`${WS}/${id}?token=${token}`)
    ws.binaryType = "arraybuffer"
    wsRef.current = ws

    ws.onopen = () => {
      console.log("✅ WS connected")
      setConnected(true)
    }

    ws.onclose = () => {
      console.log("❌ WS disconnected")
      setConnected(false)
    }

    ws.onerror = (e) => {
      console.error("❌ WS error", e)
    }

    ws.onmessage = (event) => {
      const update = new Uint8Array(event.data)
      Y.applyUpdate(ydoc, update)
    }

    // --- LOCAL → REMOTE ---
    ydoc.on("update", (update: Uint8Array) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(update)
      }
    })

    // --- Yjs → textarea ---
    ytext.observe(() => {
      if (!textareaRef.current) return
      textareaRef.current.value = ytext.toString()
    })

    // --- textarea → Yjs ---
    const onInput = () => {
      if (!textareaRef.current) return

      const value = textareaRef.current.value

      ydoc.transact(() => {
        ytext.delete(0, ytext.length)
        ytext.insert(0, value)
      })
    }

    textareaRef.current?.addEventListener("input", onInput)

    return () => {
      console.log("🧹 cleanup")

      textareaRef.current?.removeEventListener("input", onInput)

      ws.close()
      ydoc.destroy()
    }
  }, [id])

  return (
    <div>
      <h2>Editor #{id}</h2>
      <p>Status: {connected ? "🟢 connected" : "🔴 disconnected"}</p>
      <button onClick={() => setShowShare(true)}>Share</button>

      {showShare && <ShareForm onClose={() => setShowShare(false)} />}

      <textarea
        ref={textareaRef}
        style={{ width: "100%", height: 300 }}
        placeholder="Start typing..."
      />
    </div>
  )
}