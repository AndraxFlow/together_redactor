import { useState } from "react";
import { useAuth } from "../auth/useAuth";

export function RegisterForm() {
  const { register } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      await register({ email, password });

      setSuccess("Аккаунт создан. Теперь можно войти.");
      setEmail("");
      setPassword("");
    } catch (err: any) {
      const msg =
        err?.response?.data?.detail ||
        "Ошибка регистрации (возможно email уже занят)";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="card form" onSubmit={onSubmit}>
      <h2>Регистрация</h2>

      <label>
        Email
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
      </label>

      <label>
        Пароль
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
      </label>

      {success && <p className="success">{success}</p>}
      {error && <p className="error">{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? "Создаем..." : "Зарегистрироваться"}
      </button>
    </form>
  );
}