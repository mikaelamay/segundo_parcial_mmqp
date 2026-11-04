"""Genera las capturas de pantalla del informe usando Chromium + Playwright.

Requiere que la aplicación esté corriendo en http://127.0.0.1:5000
"""
import html as html_lib
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:5000"
RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "docs" / "capturas"
TERMINAL = RAIZ / "docs" / "terminal"
DB = RAIZ / "instance" / "medicontrol.db"

SALIDA.mkdir(parents=True, exist_ok=True)


def nueva_pagina(browser):
    page = browser.new_page(viewport={"width": 1120, "height": 900})
    page.on("dialog", lambda dialogo: dialogo.accept())
    return page


def capturar(page, ruta, nombre):
    page.goto(BASE + ruta, wait_until="networkidle")
    page.add_style_tag(content="html { font-size: 17px; }")
    page.wait_for_timeout(250)
    page.screenshot(
        path=str(SALIDA / nombre), full_page=True, animations="disabled"
    )
    print("Captura:", nombre)


def capturar_actual(page, nombre):
    page.add_style_tag(content="html { font-size: 17px; }")
    page.wait_for_timeout(250)
    page.screenshot(
        path=str(SALIDA / nombre), full_page=True, animations="disabled"
    )
    print("Captura:", nombre)


def render_terminal(page, archivo, titulo, nombre):
    page.set_viewport_size({"width": 1120, "height": 320})
    texto = (TERMINAL / archivo).read_text(encoding="utf-8")
    lineas = []
    for linea in texto.splitlines():
        clase = ""
        if linea.startswith("$ "):
            clase = "cmd"
        elif "INFO" in linea:
            clase = "info"
        lineas.append(
            f'<span class="{clase}">{html_lib.escape(linea) or "&nbsp;"}</span>'
        )
    contenido = "\n".join(lineas)
    documento = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><style>
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; padding: 26px; background: #e2e8f0;
    font-family: "DejaVu Sans", sans-serif;
  }}
  .ventana {{
    max-width: 1080px; margin: 0 auto; border-radius: 12px; overflow: hidden;
    box-shadow: 0 18px 45px rgba(15, 23, 42, .25); border: 1px solid #94a3b8;
    background: #0b1220;
  }}
  .barra {{
    background: #1e293b; padding: 10px 14px; display: flex; align-items: center;
    gap: 8px; border-bottom: 1px solid #334155;
  }}
  .punto {{ width: 11px; height: 11px; border-radius: 50%; display: inline-block; }}
  .rojo {{ background: #ef4444; }} .amarillo {{ background: #f59e0b; }}
  .verde {{ background: #22c55e; }}
  .titulo {{ color: #cbd5e1; font-size: 13px; margin-left: 10px; }}
  pre {{
    margin: 0; padding: 20px 22px; color: #e2e8f0; font-size: 16px;
    line-height: 1.5; font-family: "DejaVu Sans Mono", monospace;
    white-space: pre; overflow-x: auto;
  }}
  .cmd {{ color: #6ee7b7; font-weight: 700; }}
  .info {{ color: #fcd34d; }}
</style></head>
<body><div class="ventana">
  <div class="barra">
    <span class="punto rojo"></span><span class="punto amarillo"></span>
    <span class="punto verde"></span>
    <span class="titulo">{html_lib.escape(titulo)} — mayte@debian: ~/examen_2doparcialemergentes</span>
  </div>
  <pre>{contenido}</pre>
</div></body></html>"""
    page.set_content(documento, wait_until="load")
    page.wait_for_timeout(150)
    page.screenshot(
        path=str(SALIDA / nombre), full_page=True, animations="disabled"
    )
    print("Captura:", nombre)
    page.set_viewport_size({"width": 1120, "height": 900})


def main():
    hoy = date.today()
    fecha_cita = hoy + timedelta(days=3)
    fecha_iso = fecha_cita.strftime("%Y-%m-%d")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path="/usr/bin/chromium",
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = nueva_pagina(browser)

        # ---------- PARTE 1 ----------
        capturar(page, "/", "01_panel_principal.png")
        render_terminal(
            page, "estructura.txt", "Estructura del proyecto",
            "02_estructura_proyecto.png",
        )

        # ---------- PARTE 3: vistas ----------
        capturar(page, "/medicos/", "03_medicos_listado.png")
        capturar(page, "/medicos/nuevo", "04_medicos_formulario.png")
        capturar(page, "/medicos/?q=cardio", "05_medicos_busqueda.png")
        capturar(page, "/pacientes/", "06_pacientes_listado.png")
        capturar(page, "/pacientes/1/editar", "07_paciente_edicion.png")
        capturar(page, "/citas/", "08_citas_listado.png")
        capturar(page, "/citas/nueva", "09_citas_formulario.png")
        capturar(page, "/citas/1/editar", "10_citas_edicion.png")

        # ---------- PARTE 2: base de datos ----------
        render_terminal(
            page, "migraciones.txt", "Migraciones con Flask-Migrate",
            "11_migraciones.png",
        )
        render_terminal(
            page, "esquema_bd.txt", "Esquema de la base de datos SQLite",
            "12_esquema_bd.png",
        )

        # ---------- PARTE 4: operaciones ----------
        render_terminal(
            page, "datos_prueba.txt", "Carga de datos de prueba",
            "13_datos_prueba.png",
        )

        # Crear paciente desde la interfaz
        page.goto(BASE + "/pacientes/nuevo", wait_until="networkidle")
        page.fill("#nombre", "Valeria Quispe Rojas")
        page.fill("#telefono", "70998877")
        page.click("button[type=submit]")
        page.wait_for_url("**/pacientes/")
        page.wait_for_timeout(350)
        capturar_actual(page, "14_paciente_creado.png")

        # Crear cita desde la interfaz
        page.goto(BASE + "/citas/nueva", wait_until="networkidle")
        page.fill("#fecha", fecha_iso)
        page.fill("#hora", "13:00")
        page.select_option("#medico_id", label="Dr. Marco Condori · Medicina General")
        page.select_option("#paciente_id", label="Valeria Quispe Rojas · 70998877")
        capturar_actual(page, "15_cita_formulario_lleno.png")

        page.click("button[type=submit]")
        page.wait_for_url("**/citas/")
        page.wait_for_timeout(350)
        capturar_actual(page, "16_cita_creada.png")

        # Intento de cita duplicada (mismo médico, fecha y hora)
        page.goto(BASE + "/citas/nueva", wait_until="networkidle")
        page.fill("#fecha", fecha_iso)
        page.fill("#hora", "13:00")
        page.select_option("#medico_id", label="Dr. Marco Condori · Medicina General")
        page.select_option("#paciente_id", label="Valeria Quispe Rojas · 70998877")
        page.click("button[type=submit]")
        page.wait_for_timeout(500)
        capturar_actual(page, "17_validacion_duplicada.png")

        # Obtener el id de la cita creada
        conexion = sqlite3.connect(DB)
        fila = conexion.execute(
            "SELECT c.id FROM citas c "
            "JOIN pacientes p ON p.id = c.paciente_id "
            "WHERE p.nombre = ? ORDER BY c.id DESC LIMIT 1",
            ("Valeria Quispe Rojas",),
        ).fetchone()
        conexion.close()
        cita_id = fila[0]

        # Editar la cita
        page.goto(BASE + f"/citas/{cita_id}/editar", wait_until="networkidle")
        capturar_actual(page, "18_cita_edicion_formulario.png")
        page.fill("#hora", "14:30")
        page.click("button[type=submit]")
        page.wait_for_url("**/citas/")
        page.wait_for_timeout(350)
        capturar_actual(page, "19_cita_actualizada.png")

        # Eliminar la cita
        fila_cita = page.locator("tr", has_text="Valeria Quispe Rojas")
        fila_cita.locator("form[action$='/eliminar'] button").click()
        page.wait_for_timeout(500)
        capturar_actual(page, "20_cita_eliminada.png")

        # Eliminar el paciente
        page.goto(BASE + "/pacientes/", wait_until="networkidle")
        fila_paciente = page.locator("tr", has_text="Valeria Quispe Rojas")
        fila_paciente.locator("form[action$='/eliminar'] button").click()
        page.wait_for_timeout(500)
        capturar_actual(page, "21_paciente_eliminado.png")

        # Intento de eliminar un médico con citas
        page.goto(BASE + "/medicos/", wait_until="networkidle")
        fila_medico = page.locator("tr", has_text="Dra. Ana Torres")
        fila_medico.locator("form[action$='/eliminar'] button").click()
        page.wait_for_timeout(500)
        capturar_actual(page, "22_eliminacion_bloqueada.png")

        browser.close()


if __name__ == "__main__":
    main()
