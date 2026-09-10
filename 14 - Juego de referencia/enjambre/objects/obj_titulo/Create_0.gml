/// Portada, menú, opciones y créditos. Una máquina de estados sencilla en vez de
/// cuatro objetos que se pisan (04 · 02 §5.9).
estado = "portada";      // portada · menu · opciones · creditos
opcion = 0;
tiempo = 0;
avisado = false;

opciones_menu = ["jugar", "opciones", "creditos", "salir"];
opciones_ajustes = ["idioma", "musica", "efectos", "sacudida", "pantalla", "volver"];
