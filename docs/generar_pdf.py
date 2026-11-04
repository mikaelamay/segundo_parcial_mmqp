"""Genera el PDF final del informe y numera automáticamente el índice.

Estrategia:
1. Se genera un borrador con marcadores en el índice.
2. Se extrae el texto de cada página para ubicar el inicio de cada sección.
3. Se reemplazan los marcadores por los números reales y se genera el PDF final.
4. Se agregan los metadatos del documento.
"""
import re
import unicodedata
from pathlib import Path

from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

DOCS = Path(__file__).resolve().parent
HTML = DOCS / "informe.html"
TMP_HTML = DOCS / "_informe_render.html"
BORRADOR = DOCS / "_borrador.pdf"
FINAL = DOCS / "Informe_MediControl_Mayte_Quispe_Perez.pdf"

FOOTER = """
<div style="width:100%; font-family: Arial, sans-serif; font-size:7.5pt; color:#64748b;
            padding:0 13mm; display:flex; justify-content:space-between; align-items:center;">
  <span>TEM-742 · MediControl · Mayte Mikaela Quispe Perez</span>
  <span>Página <span class="pageNumber"></span> de <span class="totalPages"></span></span>
</div>
"""

SECCIONES = {
    "{{P_INTRO}}": "introduccion y objetivos",
    "{{P_REQ}}": "verificacion de requerimientos",
    "{{P1}}": "arquitectura y configuracion",
    "{{P2}}": "modelos y migraciones",
    "{{P3}}": "crud y plantillas",
    "{{P4}}": "funcionamiento de la aplicacion",
    "{{P_CONC}}": "conclusiones",
    "{{P_ANEXO}}": "anexo — ejecucion y entregables",
}


def normalizar(texto):
    sin_tildes = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", sin_tildes).lower()


def renderizar(html_entrada, pdf_salida):
    with sync_playwright() as playwright:
        navegador = playwright.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        pagina = navegador.new_page(viewport={"width": 1200, "height": 1600})
        pagina.goto(Path(html_entrada).as_uri(), wait_until="networkidle")
        pagina.emulate_media(media="print")
        pagina.wait_for_timeout(800)

        faltantes = pagina.evaluate(
            "Array.from(document.images)"
            ".filter(i => !i.complete || i.naturalWidth === 0)"
            ".map(i => i.getAttribute('src'))"
        )
        if faltantes:
            print("ADVERTENCIA, imágenes no cargadas:", faltantes)
        else:
            print("Todas las imágenes cargaron correctamente.")

        pagina.pdf(
            path=str(pdf_salida),
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "18mm", "left": "13mm", "right": "13mm"},
            display_header_footer=True,
            header_template="<div></div>",
            footer_template=FOOTER,
        )
        navegador.close()


def buscar_paginas(pdf):
    lector = PdfReader(str(pdf))
    paginas = [
        (numero, normalizar(pagina.extract_text() or ""))
        for numero, pagina in enumerate(lector.pages, start=1)
    ]

    encontradas = {}
    for marcador, texto in SECCIONES.items():
        pagina_encontrada = "—"
        for numero, contenido in paginas:
            if numero < 3:
                continue
            if texto in contenido:
                pagina_encontrada = str(numero)
                break
        encontradas[marcador] = pagina_encontrada
    return encontradas, len(paginas)


def main():
    html_original = HTML.read_text(encoding="utf-8")

    # Primera pasada: borrador con marcadores visibles.
    borrador_html = html_original
    for marcador in SECCIONES:
        borrador_html = borrador_html.replace(marcador, "00")
    TMP_HTML.write_text(borrador_html, encoding="utf-8")
    renderizar(TMP_HTML, BORRADOR)

    paginas, total = buscar_paginas(BORRADOR)
    print("Páginas del borrador:", total)
    print("Inicio de secciones:", paginas)

    # Segunda pasada: números reales.
    final_html = html_original
    for marcador, numero in paginas.items():
        final_html = final_html.replace(marcador, numero)
    TMP_HTML.write_text(final_html, encoding="utf-8")
    renderizar(TMP_HTML, FINAL)

    # Verificación: si al cambiar los marcadores cambió la paginación,
    # se corrigen los números y se vuelve a generar.
    paginas_finales, _ = buscar_paginas(FINAL)
    if paginas_finales != paginas:
        print("Ajustando numeración del índice:", paginas_finales)
        final_html = html_original
        for marcador, numero in paginas_finales.items():
            final_html = final_html.replace(marcador, numero)
        TMP_HTML.write_text(final_html, encoding="utf-8")
        renderizar(TMP_HTML, FINAL)

    # Metadatos del PDF.
    lector = PdfReader(str(FINAL))
    escritor = PdfWriter()
    for pagina in lector.pages:
        escritor.add_page(pagina)
    escritor.add_metadata(
        {
            "/Title": "MediControl — Sistema de gestión de médicos y citas médicas",
            "/Author": "Mayte Mikaela Quispe Perez",
            "/Subject": "Segundo Parcial Práctico — TEM-742 Tecnologías Emergentes II",
            "/Keywords": "Flask, SQLAlchemy, Flask-Migrate, Bootstrap, SQLite, MediControl",
            "/Creator": "Informe generado con HTML + Chromium",
        }
    )
    with open(FINAL, "wb") as archivo:
        escritor.write(archivo)

    TMP_HTML.unlink(missing_ok=True)
    BORRADOR.unlink(missing_ok=True)
    print("PDF final:", FINAL)
    print("Páginas finales:", len(lector.pages))


if __name__ == "__main__":
    main()
