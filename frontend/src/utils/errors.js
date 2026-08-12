/**
 * Surfaces DRF's actual validation/error message (e.g. "Credenciais
 * inválidas.", "user with this email already exists.") instead of the
 * generic axios "Request failed with status code NNN" text.
 * @param {*} error - an Axios error (reads `error.response.data`)
 * @returns {string|null} the first usable error message found, or null if
 *   the error has no DRF-shaped response body
 */
export function extractErrorMessage(error) {
  const data = error.response?.data;
  if (!data) return null;
  if (typeof data.detail === "string") return data.detail;
  const firstValue = Object.values(data)[0];
  if (Array.isArray(firstValue)) return firstValue[0];
  return typeof firstValue === "string" ? firstValue : null;
}
