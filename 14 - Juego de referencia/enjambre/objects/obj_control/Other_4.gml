// Room Start: la cámara vuelve a su sitio en cada sala. Sin esto, una sacudida a
// medias al cambiar de sala deja el mundo torcido para siempre.
global.sacudida = 0;
global.congelado = 0;

global.transicion = false;   // la sala nueva ya está: se vuelve a aceptar entrada
