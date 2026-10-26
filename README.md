# competicionhyrox.es

Web informativa (no oficial) sobre las competiciones HYROX en España. Se publica gratis con GitHub Pages.

## Cómo está organizada

- `src/` — el texto de cada página (aquí se edita el contenido).
- `data/competiciones.json` — el calendario: fechas, sedes y resumen de cada prueba.
- `assets/` — estilos, código de la calculadora, fotos y vídeo.
- `build.py` — junta todo y genera las páginas finales (`index.html`, `calendario/`, etc.).

## Actualizar el calendario

1. Edita `data/competiciones.json` (añadir una prueba o escribir su `resumen`).
2. Ejecuta `python3 build.py`.
3. Sube los cambios a GitHub.

Las pruebas pasan solas de "Próximas" a "Ya celebradas" cuando acaba su fecha (al volver a generar la web).

## Imágenes

Las fotos y el vídeo son ilustrativos, generados con IA para esta web. No muestran personas ni eventos reales.
