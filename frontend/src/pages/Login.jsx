import "./Login.css";
import WelcomePanel from "../components/layout/WelcomePanel";
import JoinForm from "../components/layout/JoinForm";
import GoogleButton from "../components/layout/GoogleButton";
import { useEffect, useState } from "react";
import joinBackground from "../assets/join-background.png";

export default function Login() {
  useEffect(() => {
    localStorage.removeItem("token");
  }, []);

  return (
    <div className="login">
      <WelcomePanel />
      <section className="login__form">
        <img
          className="login__form-background"
          src={joinBackground}
          alt=""
        />
        <p className="login__title">Entrar</p>
        <JoinForm
          pathTo="/signup"
          accountText="Não tem conta?"
          linkText="Cadastre-se"
          buttonText="Entrar"
          formType="login"
        />
        <div className="login__divider">
          <span className="login__divider-text">ou</span>
        </div>
        <GoogleButton />
      </section>
    </div>
  );
}
