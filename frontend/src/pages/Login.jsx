import "./Login.css";
import WelcomePanel from "../components/layout/WelcomePanel";
import JoinForm from "../components/layout/JoinForm";
import GoogleButton from "../components/layout/GoogleButton";

export default function Login() {
  return (
    <div className="login">
      <WelcomePanel />
      <section className="login__form">
        <p className="login__title">Entrar</p>
        <JoinForm
          pathTo="/signup"
          accountText="Não tem conta?"
          linkText="Cadastre-se"
          buttonText="Entrar"
          formType="login"
        />
        <div className="login__divider">
          <span className="login__divider_text">ou</span>
        </div>
        <GoogleButton />
      </section>
    </div>
  );
}
