import LoadingSpinner from "./LoadingSpinner";
import "./LoadingOverlay.css";

export default function LoadingOverlay() {
  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <LoadingSpinner />
    </div>
  );
}
