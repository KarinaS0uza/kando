// Surfaces DRF's actual validation/error message (e.g. "Credenciais
// inválidas.", "user with this email already exists.") instead of the
// generic axios "Request failed with status code NNN" text.
export function extractErrorMessage(error) {
  const data = error.response?.data;
  if (!data) return null;
  if (typeof data.detail === "string") return data.detail;
  const firstValue = Object.values(data)[0];
  if (Array.isArray(firstValue)) return firstValue[0];
  return typeof firstValue === "string" ? firstValue : null;
}
