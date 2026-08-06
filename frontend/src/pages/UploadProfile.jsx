import Header from "../components/layout/Header";
import "./UploadProfile.css";
import InputUpload from "../components/layout/InputUpload";
import { useState } from "react";
import textFieldIcon from "../assets/text-field.svg";
import { useNavigate } from "react-router-dom";
import { login, createJobPosting, createResume } from "../services/api";
import { setUploadPromises } from "../utils/uploadTracker";

export default function UploadProfile() {
  const [resumeFile, setResumeFile] = useState(null);
  const [resumeText, setResumeText] = useState(null);

  const [jobFile, setJobFile] = useState(null);
  const [jobText, setJobText] = useState(null);

  const navigate = useNavigate();

  function isTextInvalid(text) {
    return !text || text.length < 150 || text.length > 3500;
  }

  function getTextError(text) {
    if (!text) return null;
    if (text.length < 150) {
      return `Mínimo de 150 caracteres (${text.length}/150)`;
    }
    if (text.length > 3500) {
      return `Máximo de 3500 caracteres excedido (${text.length}/3500)`;
    }
    return null;
  }

  const resumeOk = resumeFile || !isTextInvalid(resumeText);
  const jobOk = jobFile || !isTextInvalid(jobText);

  const handleSubmit = (e) => {
    e.preventDefault();
    const jobP = createJobPosting(jobFile || jobText);
    const resumeP = createResume(resumeFile || resumeText);
    setUploadPromises(jobP, resumeP);
    navigate("/upload/reliability");
  };

  return (
    <>
      <Header menuActive={false} />
      <div className="upload">
        <h1 className="upload__title">Compare suas habilidades</h1>
        <form className="upload__inputs" onSubmit={handleSubmit}>
          <div className="upload__inputs-pdf">
            <p className="upload__input-title">Meu currículo</p>
            <div
              className={`upload__pdf-collapse${
                resumeText ? " upload__pdf-collapse_collapsed" : ""
              }`}
            >
              <div className="upload__pdf-collapse__inner">
                <InputUpload onFileChange={setResumeFile} />
              </div>
            </div>
            <div
              className={`upload__pdf-collapse${
                resumeFile ? " upload__pdf-collapse_collapsed" : ""
              }`}
            >
              <div className="upload__pdf-collapse__inner">
                {!resumeText && <p className="upload__ou">ou</p>}
                <div className="upload__txt-wrap">
                  <textarea
                    className={
                      resumeText
                        ? "upload__input-txt upload__input-text_solid"
                        : "upload__input-txt"
                    }
                    placeholder="Cole aqui seu currículo"
                    onChange={(e) => setResumeText(e.target.value)}
                  ></textarea>
                  <div className="upload__txt-placeholder" aria-hidden="true">
                    <img
                      className="upload__txt-icon"
                      src={textFieldIcon}
                      alt=""
                    />
                    <p>Copie e cole seu currículo aqui</p>
                  </div>
                  <p className="upload__input-error">
                    {getTextError(resumeText)}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div className="vertical-line"></div>
          <div className="upload__inputs-pdf">
            <p className="upload__input-title">Descrição da vaga</p>
            <div
              className={`upload__pdf-collapse${
                jobText ? " upload__pdf-collapse_collapsed" : ""
              }`}
            >
              <div className="upload__pdf-collapse__inner">
                <InputUpload onFileChange={setJobFile} />
              </div>
            </div>
            <div
              className={`upload__pdf-collapse${
                jobFile ? " upload__pdf-collapse_collapsed" : ""
              }`}
            >
              <div className="upload__pdf-collapse__inner">
                {!jobText && <p className="upload__ou">ou</p>}
                <div className="upload__txt-wrap">
                  <textarea
                    className={
                      jobText
                        ? "upload__input-txt upload__input-text_solid"
                        : "upload__input-txt"
                    }
                    placeholder="Cole aqui a descrição da vaga"
                    onChange={(e) => setJobText(e.target.value)}
                  ></textarea>
                  <div className="upload__txt-placeholder" aria-hidden="true">
                    <img
                      className="upload__txt-icon"
                      src={textFieldIcon}
                      alt=""
                    />
                    <p>Copie e cole a vaga aqui</p>
                  </div>
                  <p className="upload__input-error">{getTextError(jobText)}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="upload__compare-button-wrap">
            <button
              className="upload__compare-button"
              disabled={!resumeOk || !jobOk}
              onClick={handleSubmit}
            >
              Avançar
            </button>
          </div>
        </form>
      </div>
    </>
  );
}
