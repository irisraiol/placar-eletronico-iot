/**
 * Cliente HTTP simples para a API do Placar Eletrônico IoT.
 * Encapsula fetch + tratamento de erro padrão.
 */
const API_BASE = (() => {
  // Quando o frontend é servido pelo próprio FastAPI usamos caminho relativo.
  // Caso esteja sendo aberto via file:// ou Live Server, ajuste aqui.
  if (location.protocol === "file:") return "http://localhost:8000";
  return "";
})();
async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    let detalhe = res.statusText;
    try { detalhe = (await res.json()).detail || detalhe; } catch (_) {}
    throw new Error(`[${res.status}] ${detalhe}`);
  }
  if (res.status === 204) return null;
  return res.json();
}
export const api = {
  listarPartidas: ()           => request("/api/partidas"),
  obterPartida:   (id)         => request(`/api/partidas/${id}`),
  criarPartida:   (payload)    => request("/api/partidas",
                                  { method: "POST", body: JSON.stringify(payload) }),
  deletarPartida: (id)         => request(`/api/partidas/${id}`, { method: "DELETE" }),
  enviarEvento:   (id, evento) => request(`/api/partidas/${id}/eventos`,
                                  { method: "POST", body: JSON.stringify(evento) }),
};
/** Formata segundos em mm:ss. */
export function formatarTempo(segundos) {
  const m = Math.floor(segundos / 60).toString().padStart(2, "0");
  const s = Math.floor(segundos % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}
/** Mostra um alerta dentro de um container. */
export function mostrarErro(container, msg) {
  if (!container) return;
  container.innerHTML = `<div class="alert">${msg}</div>`;
}