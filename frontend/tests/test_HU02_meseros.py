import sys
import subprocess
from playwright.sync_api import sync_playwright


def login(page):

    page.goto("http://127.0.0.1:8000/admin/")

    page.wait_for_selector(".login-container")

    page.locator(
        "input[name='usuario']"
    ).fill("bistro")

    page.locator(
        "input[name='contrasena']"
    ).fill("12345")

    page.locator(
        "button[type='submit']"
    ).click()

    page.wait_for_timeout(2000)


def ir_meseros(page):

    page.locator(
        "#bmNav button[data-section='Meseros']"
    ).click()

    page.wait_for_timeout(2000)


def abrir_form(page):

    page.evaluate(
        "document.dispatchEvent(new CustomEvent('bm:meseros:add'))"
    )

    page.wait_for_timeout(1500)


def limpiar_mesero(usuario):
    """
    Usa el mismo python del venv (sys.executable)
    para que Django esté disponible al limpiar.
    """

    subprocess.run([
        sys.executable, "manage.py", "shell", "-c",
        f"from django.apps import apps; "
        f"M = apps.get_model('BistroMaster', 'Mesero'); "
        f"M.objects.filter(usuario='{usuario}').delete(); "
        f"print('Limpieza: {usuario} eliminado')"
    ])


def test_HU02_meseros():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=700
        )

        page = browser.new_page()

        print("\n========================================")
        print("      HU-02: Gestión Meseros")
        print("========================================")

        login(page)

        ir_meseros(page)

        # =====================================================
        # CP-F12: Crear mesero
        # =====================================================
        print("\n--- CP-F12: Crear mesero ---")

        abrir_form(page)

        form = page.locator(
            "[data-section='Meseros'] [data-emp-form]"
        )

        form.locator(
            "input[name='nombre']"
        ).fill("Mesa Uno")

        form.locator(
            "input[name='usuario']"
        ).fill("mesa1")

        form.locator(
            "input[name='contrasena']"
        ).fill("12345")

        form.locator(
            "input[name='confirmar_contrasena']"
        ).fill("12345")

        form.locator(
            "select[name='contrato']"
        ).select_option(index=1)

        form.locator(
            "button[type='submit']"
        ).last.click()

        page.wait_for_timeout(3500)

        contenido = page.locator(
            "body"
        ).inner_text()

        if (
            "Mesa Uno" in contenido
            or not form.is_visible()
        ):

            print(
                "[✅] CP-F12 PASÓ: Mesero creado"
            )

        else:

            print(
                "[❌] CP-F12 FALLÓ: No creó"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf12_crear_mesero.png"
        )

        # =====================================================
        # CP-F13: Campos incompletos
        # =====================================================
        print("\n--- CP-F13: Campos incompletos ---")

        abrir_form(page)

        form = page.locator(
            "[data-section='Meseros'] [data-emp-form]"
        )

        form.locator(
            "button[type='submit']"
        ).last.click()

        page.wait_for_timeout(1500)

        if form.locator(
            "input[name='nombre']"
        ).is_visible():

            print(
                "[✅] CP-F13 PASÓ: Validación obligatoria"
            )

        else:

            print(
                "[❌] CP-F13 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf13_campos_incompletos.png"
        )

        # =====================================================
        # CP-F14: Contraseñas distintas
        # =====================================================
        print("\n--- CP-F14: Contraseñas distintas ---")

        form.locator(
            "input[name='nombre']"
        ).fill("Mesa Error")

        form.locator(
            "input[name='usuario']"
        ).fill("mesa2")

        form.locator(
            "input[name='contrasena']"
        ).fill("12345")

        form.locator(
            "input[name='confirmar_contrasena']"
        ).fill("00000")

        form.locator(
            "select[name='contrato']"
        ).select_option(index=1)

        form.locator(
            "button[type='submit']"
        ).last.click()

        page.wait_for_timeout(2000)

        contenido = page.locator(
            "body"
        ).inner_text()

        if "coinciden" in contenido.lower():

            print(
                "[✅] CP-F14 PASÓ: Detectó error"
            )

        else:

            print(
                "[❌] CP-F14 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf14_contrasenas_distintas.png"
        )

        # =====================================================
        # CP-F15: Cancelar formulario
        # =====================================================
        print("\n--- CP-F15: Cancelar formulario ---")

        page.locator(
            "[data-emp-cancel]"
        ).click()

        page.wait_for_timeout(1500)

        contenido = page.locator(
            "body"
        ).inner_text()

        if "Meseros" in contenido:

            print(
                "[✅] CP-F15 PASÓ: Volvió a la lista"
            )

        else:

            print(
                "[❌] CP-F15 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf15_cancelar_formulario.png"
        )

        # =====================================================
        # CP-F16: Volver sin guardar
        # =====================================================
        print("\n--- CP-F16: Volver sin guardar ---")

        abrir_form(page)

        page.locator(
            "[data-emp-back]"
        ).click()

        page.wait_for_timeout(1500)

        contenido = page.locator(
            "body"
        ).inner_text()

        if "Meseros" in contenido:

            print(
                "[✅] CP-F16 PASÓ: Volvió a la lista"
            )

        else:

            print(
                "[❌] CP-F16 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf16_volver_sin_guardar.png"
        )

        # =====================================================
        # CP-F17: Badge disponible
        # =====================================================
        print("\n--- CP-F17: Badge disponible ---")

        page.locator(
            "[data-emp-edit]"
        ).first.click()

        page.wait_for_timeout(1500)

        form = page.locator(
            "[data-section='Meseros'] [data-emp-form]"
        )

        form.locator(
            "select[name='disponible']"
        ).select_option("false")

        form.locator(
            "button[type='submit']"
        ).last.click()

        page.wait_for_timeout(2500)

        contenido = page.locator(
            "body"
        ).inner_text()

        if "No" in contenido:

            print(
                "[✅] CP-F17 PASÓ: Badge actualizado"
            )

        else:

            print(
                "[❌] CP-F17 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf17_badge_disponible.png"
        )

        # =====================================================
        # CP-F18: Usuario duplicado
        # =====================================================
        print("\n--- CP-F18: Usuario duplicado ---")

        abrir_form(page)

        form = page.locator(
            "[data-section='Meseros'] [data-emp-form]"
        )

        form.locator(
            "input[name='nombre']"
        ).fill("Mesa Dup")

        form.locator(
            "input[name='usuario']"
        ).fill("mesa1")

        form.locator(
            "input[name='contrasena']"
        ).fill("12345")

        form.locator(
            "input[name='confirmar_contrasena']"
        ).fill("12345")

        form.locator(
            "select[name='contrato']"
        ).select_option(index=1)

        form.locator(
            "button[type='submit']"
        ).last.click()

        page.wait_for_timeout(2500)

        contenido = page.locator(
            "body"
        ).inner_text()

        if (
            "existe" in contenido.lower()
            or "duplic" in contenido.lower()
        ):

            print(
                "[✅] CP-F18 PASÓ: Detectó duplicado"
            )

        else:

            print(
                "[❌] CP-F18 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf18_usuario_duplicado.png"
        )

        # =====================================================
        # LIMPIEZA FINAL
        # =====================================================
        print("\n--- Limpieza final ---")

        browser.close()

        limpiar_mesero("mesa1")
        limpiar_mesero("mesa2")

        print("\n========================================")
        print("      HU-02: 7 casos ejecutados")
        print("========================================\n")


if __name__ == "__main__":
    test_HU02_meseros()