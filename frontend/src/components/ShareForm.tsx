import { useState } from "react";
import { useParams } from "react-router-dom";

interface ShareFormProps {
  onClose: () => void;
}

export function ShareForm({ onClose }: ShareFormProps) {
  const { id } = useParams<{ id: string }>();
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("editor");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const token = localStorage.getItem("together_redactor_token");
      const response = await fetch(`http://localhost:8000/documents/${id}/share`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ email, role }),
      });

      if (!response.ok) {
        throw new Error("Failed to share");
      }

      setSuccess("Access granted!");
      setEmail("");
    } catch (err: any) {
      setError(err.message || "Error sharing document");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <h3>Share Document</h3>
        <form onSubmit={handleSubmit}>
          <label>
            Email:
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </label>
          <label>
            Role:
            <select value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="viewer">Viewer</option>
              <option value="editor">Editor</option>
            </select>
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Sharing..." : "Share"}
          </button>
          <button type="button" onClick={onClose}>
            Close
          </button>
        </form>
        {error && <p style={{ color: "red" }}>{error}</p>}
        {success && <p style={{ color: "green" }}>{success}</p>}
      </div>
    </div>
  );
}