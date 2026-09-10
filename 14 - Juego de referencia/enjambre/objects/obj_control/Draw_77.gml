/// Post-Draw. Vacío a propósito.
///
/// Aquí vivía la captura de pantalla, movida desde el Step porque en Post-Draw la
/// `application_surface` está viva y parecía el sitio correcto. Medido: las dos
/// capturas salieron NEGRAS, también la de `screen_save()` que llevaba toda la
/// sesión funcionando desde el Step. Se revirtió. Queda escrito para que nadie
/// vuelva a intentarlo pensando que es una mejora.
