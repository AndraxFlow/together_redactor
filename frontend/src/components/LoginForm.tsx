import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";

export function LoginForm() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login({ username, password });
      navigate("/documents");
    } catch (err) {
      setError("Не удалось войти. Проверь email и пароль.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h2>Вход</h2>

      <label>
        Email
        <input
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          type="email"
          placeholder="user@example.com"
          autoComplete="email"
          required
        />
      </label>

      <label>
        Пароль
        <input
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          type="password"
          placeholder="••••••••"
          autoComplete="current-password"
          required
        />
      </label>

      {error ? <p className="error">{error}</p> : null}

      <button type="submit" disabled={loading}>
        {loading ? "Входим..." : "Войти"}
      </button>
    </form>
  );
}