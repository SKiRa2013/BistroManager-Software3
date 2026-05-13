import sys
import subprocess
from playwright.sync_api import sync_playwright


def login(page):
    page.goto("http://127.0.0.1:8000/admin/")
    page.wait_for_selector(".login-container")
    page.locator("input[name='usuario']").fill("bistro")
    page.locator("input[name='contrasena']").fill("12345")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(2000)


def limpiar(modelo, usuario):
    subprocess.run([
        sys.executable, "manage.py", "shell", "-c",
        f"from django.apps import apps; "
        f"M = apps.get_model('BistroMaster', '{modelo}'); "
        f"M.objects.filter(usuario='{usuario}').delete(); "
        f"print('Limpieza: {usuario} eliminado')"
    ])


def test_HU03_estado_personal():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=700)
        page = browser.new_page()

        print("\n========================================")
        print("   HU-03: Activar/Desactivar Personal")
        print("========================================")

        login(page)

        # --- Crear mesero de prueba ---
        page.locator("#bmNav button[data-section='Meseros']").click()
        page.wait_for_timeout(1500)
        page.evaluate("document.dispatchEvent(new CustomEvent('bm:meseros:add'))")
        page.wait_for_timeout(1500)

        form = page.locator("[data-section='Meseros'] [data-emp-form]")
        form.locator("input[name='nombre']").fill("Mesero HU03")
        form.locator("input[name='usuario']").fill("meserohu03")
        form.locator("input[name='contrasena']").fill("12345")
        form.locator("input[name='confirmar_contrasena']").fill("12345")
        form.locator("select[name='contrato']").select_option(index=1)
        form.locator("select[name='disponible']").select_option("true")
        form.locator("button[type='submit']").last.click()
        page.wait_for_timeout(2000)
        print("[✅] Mesero de prueba creado")

        # =====================================================
        # CP-F23: Desactivar mesero
        # =====================================================
        print("\n--- CP-F23: Desactivar mesero ---")
        page.locator("[data-emp-edit]").first.click()
        page.wait_for_timeout(1500)

        form = page.locator("[data-section='Meseros'] [data-emp-form]")
        form.locator("select[name='disponible']").select_option("false")
        form.locator("button[type='submit']").last.click()
        page.wait_for_timeout(2000)

        badge = page.locator("[data-emp-tbody] .bm-badge").first
        texto = badge.inner_text()
        if texto == "No":
            print("[✅] CP-F23 PASÓ: Badge cambió a 'No'")
        else:
            print(f"[❌] CP-F23 FALLÓ: Badge muestra '{texto}'")
        page.screenshot(path="frontend/tests/evidencias/cpf23_desactivar_mesero.png")

        # =====================================================
        # CP-F24: Activar mesero
        # =====================================================
        print("\n--- CP-F24: Activar mesero ---")
        page.locator("[data-emp-edit]").first.click()
        page.wait_for_timeout(1500)

        form = page.locator("[data-section='Meseros'] [data-emp-form]")
        form.locator("select[name='disponible']").select_option("true")
        form.locator("button[type='submit']").last.click()
        page.wait_for_timeout(2000)

        badge = page.locator("[data-emp-tbody] .bm-badge").first
        texto = badge.inner_text()
        if texto == "Sí":
            print("[✅] CP-F24 PASÓ: Badge volvió a 'Sí'")
        else:
            print(f"[❌] CP-F24 FALLÓ: Badge muestra '{texto}'")
        page.screenshot(path="frontend/tests/evidencias/cpf24_activar_mesero.png")

        # --- Eliminar mesero de prueba ---
        page.locator("[data-emp-edit]").first.click()
        page.wait_for_timeout(1000)
        page.locator("[data-emp-delete]").click()
        page.wait_for_timeout(1500)
        print("[✅] Mesero de prueba eliminado")

        # --- Crear domiciliario de prueba ---
        page.locator("#bmNav button[data-section='Domiciliarios']").click()
        page.wait_for_timeout(1500)
        page.evaluate("document.dispatchEvent(new CustomEvent('bm:domiciliarios:add'))")
        page.wait_for_timeout(1500)

        form = page.locator("[data-section='Domiciliarios'] [data-dom-form]")
        form.locator("input[name='nombre']").fill("Dom HU03")
        form.locator("input[name='usuario']").fill("domhu03")
        form.locator("input[name='contrasena']").fill("12345")
        form.locator("input[name='confirmar_contrasena']").fill("12345")
        form.locator("select[name='contrato']").select_option(index=1)
        form.locator("select[name='disponible']").select_option("true")
        form.locator("button[type='submit']").last.click()
        page.wait_for_timeout(2000)
        print("[✅] Domiciliario de prueba creado")

        # =====================================================
        # CP-F25: Desactivar domiciliario
        # =====================================================
        print("\n--- CP-F25: Desactivar domiciliario ---")
        page.locator("[data-dom-edit]").first.click()
        page.wait_for_timeout(1500)

        form = page.locator("[data-section='Domiciliarios'] [data-dom-form]")
        form.locator("select[name='disponible']").select_option("false")
        form.locator("button[type='submit']").last.click()
        page.wait_for_timeout(2000)

        badge_dom = page.locator("[data-dom-tbody] .bm-badge").first
        texto_dom = badge_dom.inner_text()
        if texto_dom == "No":
            print("[✅] CP-F25 PASÓ: Badge cambió a 'No'")
        else:
            print(f"[❌] CP-F25 FALLÓ: Badge muestra '{texto_dom}'")
        page.screenshot(path="frontend/tests/evidencias/cpf25_desactivar_domiciliario.png")

        # =====================================================
        # CP-F26: Activar domiciliario
        # =====================================================
        print("\n--- CP-F26: Activar domiciliario ---")
        page.locator("[data-dom-edit]").first.click()
        page.wait_for_timeout(1500)

        form = page.locator("[data-section='Domiciliarios'] [data-dom-form]")
        form.locator("select[name='disponible']").select_option("true")
        form.locator("button[type='submit']").last.click()
        page.wait_for_timeout(2000)

        badge_dom = page.locator("[data-dom-tbody] .bm-badge").first
        texto_dom = badge_dom.inner_text()
        if texto_dom == "Sí":
            print("[✅] CP-F26 PASÓ: Badge volvió a 'Sí'")
        else:
            print(f"[❌] CP-F26 FALLÓ: Badge muestra '{texto_dom}'")
        page.screenshot(path="frontend/tests/evidencias/cpf26_activar_domiciliario.png")

        # --- Limpiar ---
        print("\n--- Limpieza final ---")
        browser.close()
        limpiar("Domiciliario", "domhu03")

        print("\n========================================")
        print("   HU-03: 4 casos ejecutados")
        print("========================================\n")


if __name__ == "__main__":
    test_HU03_estado_personal()