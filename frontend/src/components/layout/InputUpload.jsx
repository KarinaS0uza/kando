import "./InputUpload.css";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/Page/AnnotationLayer.css";
import "react-pdf/dist/Page/TextLayer.css";
import { Toaster, toast } from "react-hot-toast";

import uploadIcon from "../../assets/upload-icon.svg";
import deleteIcon from "../../assets/delete-icon.svg";

pdfjs.GlobalWorkerOptions.workerSrc = `//unpkg.com/pdfjs-dist@${pdfjs.version}/build/pdf.worker.min.mjs`;

// PDF dropzone with inline preview, used twice on the same page
// (UploadProfile) for the resume and the job posting. Props:
// - onFileChange(file: File | null): called with the accepted file, or
//   null when the user removes it. UploadProfile uses this to decide
//   between sending the file or the pasted-text alternative on submit.
export default function InputUpload({ onFileChange }) {
  const [file, setFile] = useState(null);
  const [numPages, setNumPages] = useState(null);

  const onDrop = useCallback(
    (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        const newFile = acceptedFiles[0];
        setFile(newFile);
        onFileChange?.(newFile);
      }
    },
    [onFileChange],
  );

  function handleErrorMessage(err, file) {
    switch (err.code) {
      case "file-too-large": {
        const message = `${file.name} excede o tamanho máximo de 5MB`;
        toast.error(message);
        return message;
      }
      case "too-many-files":
        return "Trop de fichiers";
      case "file-invalid-type":
        toast.error("Erro: formato de arquivo inválido");
        return "Erro: formato de arquivo inválido";
      default:
        return err.message;
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    multiple: false,
    maxSize: 5 * 1024 * 1024,
    getErrorMessage: (err, file) => {
      return handleErrorMessage(err, file);
    },
  });

  function handleDelete() {
    setFile(null);
    setNumPages(null);
    onFileChange?.(null);
  }

  function onDocumentLoadSuccess({ numPages }) {
    setNumPages(numPages);
  }

  return (
    <>
      <Toaster
        position="top-right"
        containerStyle={{
          top: 70,
          left: 20,
          bottom: 20,
          right: 20,
        }}
        toastOptions={{
          style: {
            background: "#1e1e2f",
            color: "#fff",
          },
          success: {
            style: { background: "#16a34a", color: "#fff" },
            iconTheme: { primary: "#fff", secondary: "#16a34a" },
          },
          error: {
            style: { background: "#dc2626", color: "#fff" },
            iconTheme: { primary: "#fff", secondary: "#dc2626" },
          },
        }}
      />
      <section
        className={[
          "upload__input",
          isDragActive && "upload__input--on-drag",
          file && "upload__input--has-file",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        {!file && (
          <div {...getRootProps({ className: "upload__dropzone" })}>
            <input {...getInputProps()} />
            {!isDragActive ? (
              <>
                <img
                  className="upload__icon"
                  src={uploadIcon}
                  alt="Upload image"
                />
                <p className="upload__text">
                  Arraste seu PDF ou clique aqui para selecioná‑lo
                </p>
              </>
            ) : (
              <img
                className="upload__icon upload__icon--on-drag"
                src={uploadIcon}
                alt="Upload image"
              />
            )}
          </div>
        )}

        {file && (
          <div className="upload__preview">
            <Document
              file={file}
              onLoadSuccess={onDocumentLoadSuccess}
              className="upload__preview-content"
            >
              <Page
                pageNumber={1}
                className="upload__preview-page"
                renderTextLayer={false}
              />
                {numPages && numPages > 1 && (
                  <p className="upload__preview-pages">
                    +{numPages - 1} página{numPages - 1 > 1 ? "s" : ""}
                  </p>
                )}
            </Document>
          </div>
        )}

        {file && (
          <ul className="upload__file-list">
            <div className="upload__file">
              <li className="upload__file-name" key={file.path}>
                Enviado: {file.name}
              </li>
              <button
                className="upload__file-delete-button"
                onClick={handleDelete}
                type="button"
              >
                <img
                  className="upload__file-delete-button-icon"
                  src={deleteIcon}
                  alt="Delete icon"
                />
              </button>
            </div>
          </ul>
        )}
      </section>
    </>
  );
}
