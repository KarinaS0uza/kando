import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import authService from "../../services/authService";
import { createUser, login } from "../../services/api";
import useAuth from "../../hooks/useAuth";
import "./JoinForm.css";

export default function JoinForm({
  pathTo,
  accountText,
  linkText,
  buttonText,
  formType,
}) {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorFullName, setErrorFullName] = useState("");
  const [errorEmail, setErrorEmail] = useState("");
  const [errorPassword, setErrorPassword] = useState("");
  const [loading, setLoading] = useState(false);
  //const { login } = useAuth();
  const navigate = useNavigate();
  const [errorClassFullName, setErrorClassFullName] = useState(false);
  const [errorClassEmail, setErrorClassEmail] = useState(false);
  const [errorClassPassword, setErrorClassPassword] = useState(false);

  function checkFullName(value) {
    if (value == "") {
      return "";
    } else if (value.trim().length < 3) {
      return "Nome inválido";
    } else {
      return "";
    }
  }

  function checkEmail(value) {
    if (value == "") {
      return "";
    } else if (!/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(value)) {
      return "E-mail inválido";
    } else {
      return "";
    }
  }

  function checkPassword(value) {
    if (value == "") {
      return "";
    } else if (value.length < 8) {
      return "Senha inválida. Mínimo de 8 caracteres";
    } else if (value.length > 100) {
      return "Senha inválida. Máximo de 100 caracteres";
    } else {
      return "";
    }
  }

  const handleFullNameChange = (e) => {
    const val = e.target.value;
    setFullName(val);
    setErrorFullName(checkFullName(val));
    setErrorClassFullName(checkFullName(val));
  };

  const handleEmailChange = (e) => {
    const val = e.target.value;
    setEmail(val);
    setErrorEmail(checkEmail(val));
    setErrorClassEmail(checkPassword(val));
  };

  const handlePasswordChange = (e) => {
    const val = e.target.value;
    setPassword(val);
    setErrorPassword(checkPassword(val));
    setErrorClassPassword(checkPassword(val));
  };

  const handleSubmit = async (e) => {
    const userInfo = {
      email: email,
      password: password,
      full_name: fullName,
    };

    e.preventDefault();
    setErrorEmail("");
    setErrorPassword("");
    setLoading(true);
    try {
      if (formType == "login") {
        const user = await login(userInfo);
        localStorage.setItem("token", user.data.access);
      } else {
        await createUser(userInfo);
        const user = await login(userInfo);
        localStorage.setItem("token", user.data.access);
      }
      navigate("/upload");
    } catch (err) {
      console.log(err);

      if (err == "Error: Este email já está cadastrado.") {
        setErrorEmail(err.message);
      } else {
        setErrorPassword(err.message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form action="" className="join__form_inputs" onSubmit={handleSubmit}>
      {formType === "signup" && (
        <div className="join__form_input-email">
          <input
            type="text"
            className={`join__form_email ${errorClassFullName ? "join__form_input-error" : ""}`}
            placeholder="Nome completo"
            required
            value={fullName}
            onChange={(e) => handleFullNameChange(e)}
          />
          {errorFullName && <p className="join__form-error">{errorFullName}</p>}
        </div>
      )}
      <div className="join__form_input-email">
        <input
          type="email"
          className={`join__form_email ${errorClassEmail ? "join__form_input-error" : ""}`}
          placeholder="Email"
          required
          value={email}
          onChange={(e) => handleEmailChange(e)}
        />
        {errorEmail && <p className="join__form-error">{errorEmail}</p>}
      </div>
      <div className="join__form_input-email">
        <input
          type="password"
          className={`join__form_password ${errorClassPassword ? "join__form_input-error" : ""}`}
          placeholder="Senha"
          required
          value={password}
          onChange={(e) => handlePasswordChange(e)}
        />
        {errorPassword && <p className="join__form-error">{errorPassword}</p>}
      </div>
      <button
        className="join__form_button"
        disabled={
          !!checkEmail(email) ||
          !!checkPassword(password) ||
          (formType === "signup" && (!fullName || !!checkFullName(fullName)))
        }
      >
        {buttonText}
      </button>
      <div className="join__create-account">
        <p className="join__account">{accountText}</p>
        <Link className="join__account_link" to={pathTo}>
          {linkText}
        </Link>
      </div>
    </form>
  );
}
