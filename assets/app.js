/* ── Configuración compartida ITe ─────────────────────────── */
const WA_BOT = '5493743434312'; // Bot Jardín América — turnos ANSES
const WA_ADMIN = '5493743454291'; // Superadmin — contacto organizaciones

/* ── Utilidades WhatsApp ──────────────────────────────────── */
function _abrirWA(numero, texto) {
  const url = `https://wa.me/${numero}?text=${encodeURIComponent(texto)}`;
  window.open(url, '_blank', 'noopener');
}

// Botones "Pedir turno" → bot de Jardín América
function irAlBot(texto) { _abrirWA(WA_BOT, texto); }

// Botones de organizaciones + burbuja flotante → superadmin
function irAlAdmin(texto) { _abrirWA(WA_ADMIN, texto); }

// Redirige a números específicos de tarjetas del tablero
function irAContactar(numero, texto) { _abrirWA(numero, texto); }