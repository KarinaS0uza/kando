import LoadingSpinner from "./LoadingSpinner";
import "./LoadingOverlay.css";

// Full-area loading state (LoadingSpinner centered over a dedicated
// wrapper), used by pages that need to occupy the whole content area while
// fetching (Score, Reliability). No props.
export default function LoadingOverlay() {
  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      <LoadingSpinner />
    </div>
  );
}
