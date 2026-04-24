import { LoginForm } from "../components/LoginForm";
import { RegisterForm } from "../components/RegisterForm";

export function LoginPage() {
  return (
    <main className="page auth-page">
      <section className="hero card">
        <h1>Together Redactor</h1>
        <p>
          Совместный редактор документов в реальном времени. На этом этапе доступны
          регистрация, вход и подготовка к редактору.
        </p>
      </section>

      <section className="auth-grid">
        <LoginForm />
        <RegisterForm />
      </section>
    </main>
  );
}