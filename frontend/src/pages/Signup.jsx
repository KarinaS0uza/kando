import "./Signup.css";
import WelcomePanel from "../components/layout/WelcomePanel";
import JoinForm from "../components/layout/JoinForm";
import GoogleButton from "../components/layout/GoogleButton";

export default function Signup() {
  return (
    <div className="signup">
      <WelcomePanel />
      <section className="signup__form">
        <p className="signup__title">Cadastrar</p>
        <JoinForm
          pathTo="/login"
          accountText="Já tem conta?"
          linkText="Entre"
          buttonText="Cadastrar"
        />
        <div className="signup__divider">
          <span className="signup__divider_text">ou</span>
        </div>
        <GoogleButton />
      </section>
    </div>
  );
}
