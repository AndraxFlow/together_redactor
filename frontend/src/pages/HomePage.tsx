import { useAuth } from "../auth/useAuth";

export function HomePage() {
  const { user, logout } = useAuth();

  return (
    <main className="page">
      <section className="card">
        <h1>Вы вошли в систему</h1>
        <p>Пользователь: {user?.email}</p>
        <button onClick={logout}>Выйти</button>
      </section>
    </main>
  );
}