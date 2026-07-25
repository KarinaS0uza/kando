// MOCK TEMPORÁRIO - substituir pela chamada real de API quando o backend existir
const MOCK_DELAY = 600;
const EXISTING_EMAILS = ["teste@kando.com", "joao@kando.com"];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

const authService = {
  async login(email, password) {
    await delay(MOCK_DELAY);
    if (email !== "teste@kando.com" || password !== "12345678") {
      throw new Error("Email ou senha inválidos.");
    }
    return { id: 1, name: "Nícolas", email };
  },

  async signup(email, password) {
    await delay(MOCK_DELAY);
    if (EXISTING_EMAILS.includes(email)) {
      throw new Error("Este email já está cadastrado.");
    }
    return { id: 2, email };
  },

  async loginWithGoogle() {
    await delay(MOCK_DELAY);
    return { id: 3, name: "Nícolas", email: "nicolas@gmail.com" };
  },
};

export default authService;
