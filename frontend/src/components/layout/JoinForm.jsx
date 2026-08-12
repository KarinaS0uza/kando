import { useEffect, useRef, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import authService from "../../services/authService";
import { createUser, login } from "../../services/api";
import useAuth from "../../hooks/useAuth";
import { extractErrorMessage } from "../../utils/errors";
import "./JoinForm.css";
import PopoverSignup from "../ui/PopoverSignup";

// DRF's built-in unique-email validator only half-translates under
// LANGUAGE_CODE=pt-br: the template is localized but the interpolated model
// name stays "user" (e.g. "user com este email já existe."), instead of a
// clean Portuguese message like the rest of the API returns. Known cases are
// translated here rather than in extractErrorMessage, which is shared with
// other pages' unrelated (already-Portuguese) errors.
const AUTH_ERROR_TRANSLATIONS = {
  "user com este email já existe.": "Este email já está cadastrado.",
};

function translateAuthError(message) {
  return AUTH_ERROR_TRANSLATIONS[message?.toLowerCase()] || message;
}

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

  const fullNameInputRef = useRef(null);
  const [fullNameAnchorEl, setFullNameAnchorEl] = useState(null);
  const [fullNamePopoverOpen, setFullNamePopoverOpen] = useState(true);

  // The ref only points at the <input> after the signup form mounts it, so
  // the popover's anchorEl is picked up here instead of at render time.
  useEffect(() => {
    if (formType === "signup") {
      setFullNameAnchorEl(fullNameInputRef.current);
    }
  }, [formType]);

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
        localStorage.setItem("user_id", user.data.user_id);
      } else {
        await createUser(userInfo);
        const user = await login(userInfo);
        localStorage.setItem("token", user.data.access);
        localStorage.setItem("user_id", user.data.user_id);
      }
      navigate("/upload");
    } catch (err) {
      console.log(err);

      const message = translateAuthError(extractErrorMessage(err) || err.message);
      if (formType !== "login" && err.response?.status === 400) {
        setErrorEmail(message);
      } else {
        setErrorPassword(message);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form action="" className="join__fields" onSubmit={handleSubmit}>
      {formType === "signup" && (
        <div className="join__field">
          <PopoverSignup
            anchorEl={fullNameAnchorEl}
            open={fullNamePopoverOpen && Boolean(fullNameAnchorEl)}
            onClose={() => setFullNamePopoverOpen(false)}
          />
          <input
            ref={fullNameInputRef}
            type="text"
            className={`join__field-input ${errorClassFullName ? "join__field-input--error" : ""}`}
            placeholder="Nome completo"
            required
            value={fullName}
            onChange={(e) => handleFullNameChange(e)}
            onFocus={() => setFullNamePopoverOpen(false)}
          />

          {errorFullName && <p className="join__field-error">{errorFullName}</p>}
        </div>
      )}
      <div className="join__field">
        <input
          type="email"
          className={`join__field-input ${errorClassEmail ? "join__field-input--error" : ""}`}
          placeholder="Email"
          required
          value={email}
          onChange={(e) => handleEmailChange(e)}
        />
        {errorEmail && <p className="join__field-error">{errorEmail}</p>}
      </div>
      <div className="join__field">
        <input
          type="password"
          className={`join__field-input-password ${errorClassPassword ? "join__field-input--error" : ""}`}
          placeholder="Senha"
          required
          value={password}
          onChange={(e) => handlePasswordChange(e)}
        />
        {errorPassword && <p className="join__field-error">{errorPassword}</p>}
      </div>
      <button
        className="join__button"
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
        <Link className="join__account-link" to={pathTo}>
          {linkText}
        </Link>
      </div>
    </form>
  );
}
