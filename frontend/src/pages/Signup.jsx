import "./Signup.css";
import WelcomePanel from "../components/layout/WelcomePanel";
import JoinForm from "../components/layout/JoinForm";
import joinBackground from "../assets/join-background.png";

export default function Signup() {
  return (
    <div className="signup">
      <WelcomePanel />
      <section className="signup__form">
        <img
          className="signup__form-background"
          src={joinBackground}
          alt=""
        />
        <p className="signup__title">Cadastrar</p>
        <JoinForm
          pathTo="/login"
          accountText="Já tem conta?"
          linkText="Entre"
          buttonText="Cadastrar"
          formType="signup"
        />
      </section>
    </div>
  );
}
