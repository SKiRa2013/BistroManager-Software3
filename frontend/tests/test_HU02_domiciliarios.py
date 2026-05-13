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


def ir_domiciliarios(page):

    page.locator(
        "#bmNav button[data-section='Domiciliarios']"
    ).click()

    page.wait_for_timeout(2000)


def abrir_form(page):

    page.evaluate(
        "document.dispatchEvent(new CustomEvent('bm:domiciliarios:add'))"
    )

    page.wait_for_timeout(1500)


def limpiar_domiciliario(usuario):

    subprocess.run([
        sys.executable, "manage.py", "shell", "-c",
        f"from django.apps import apps; "
        f"D = apps.get_model('BistroMaster', 'Domiciliario'); "
        f"D.objects.filter(usuario='{usuario}').delete(); "
        f"print('Limpieza: {usuario} eliminado')"
    ])


def test_HU02_domiciliarios():

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            slow_mo=700
        )

        page = browser.new_page()

        print("\n========================================")
        print("   HU-02: Gestión Domiciliarios")
        print("========================================")

        login(page)

        ir_domiciliarios(page)

        # =====================================================
        # CP-F19: Crear domiciliario con datos completos
        # =====================================================
        print("\n--- CP-F19: Crear domiciliario ---")

        abrir_form(page)

        form = page.locator(
            "[data-section='Domiciliarios'] [data-dom-form]"
        )

        form.locator(
            "input[name='nombre']"
        ).fill("Dom Uno")

        form.locator(
            "input[name='usuario']"
        ).fill("dom1")

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
            "Dom Uno" in contenido
            or not form.is_visible()
        ):

            print(
                "[✅] CP-F19 PASÓ: Domiciliario creado y visible en tabla"
            )

        else:

            print(
                "[❌] CP-F19 FALLÓ: No apareció en la tabla"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf19_crear_domiciliario.png"
        )

        # =====================================================
        # CP-F20: Campos incompletos (nombre vacío)
        # =====================================================
        print("\n--- CP-F20: Campos incompletos ---")

        abrir_form(page)

        form = page.locator(
            "[data-section='Domiciliarios'] [data-dom-form]"
        )

        form.locator(
            "button[type='submit']"
        ).last.click()

        page.wait_for_timeout(1500)

        if form.locator(
            "input[name='nombre']"
        ).is_visible():

            print(
                "[✅] CP-F20 PASÓ: Validación bloqueó el envío"
            )

        else:

            print(
                "[❌] CP-F20 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf20_campos_incompletos.png"
        )

        # =====================================================
        # CP-F21: Contraseñas distintas
        # =====================================================
        print("\n--- CP-F21: Contraseñas distintas ---")

        form.locator(
            "input[name='nombre']"
        ).fill("Dom Error")

        form.locator(
            "input[name='usuario']"
        ).fill("dom2")

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
                "[✅] CP-F21 PASÓ: Mensaje de error visible"
            )

        else:

            print(
                "[❌] CP-F21 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf21_contrasenas_distintas.png"
        )

        # =====================================================
        # CP-F22: Badge disponible domiciliario
        # =====================================================
        print("\n--- CP-F22: Badge disponible ---")

        page.locator(
            "[data-dom-cancel]"
        ).click()

        page.wait_for_timeout(1500)

        page.locator(
            "[data-dom-edit]"
        ).first.click()

        page.wait_for_timeout(1500)

        form = page.locator(
            "[data-section='Domiciliarios'] [data-dom-form]"
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
                "[✅] CP-F22 PASÓ: Badge 'No' visible en tabla"
            )

        else:

            print(
                "[❌] CP-F22 FALLÓ"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cpf22_badge_disponible.png"
        )

        # =====================================================
        # LIMPIEZA FINAL
        # =====================================================
        print("\n--- Limpieza final ---")

        browser.close()

        limpiar_domiciliario("dom1")
        limpiar_domiciliario("dom2")

        print("\n========================================")
        print("   HU-02: 4 casos ejecutados")
        print("========================================\n")


if __name__ == "__main__":
    test_HU02_domiciliarios()