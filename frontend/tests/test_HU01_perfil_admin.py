from playwright.sync_api import sync_playwright


def login(page):
    """Función auxiliar para hacer login rápido."""
    page.goto("http://127.0.0.1:8000/admin/")
    page.wait_for_selector(".login-container")

    page.locator(".login-container input[name='usuario']").fill("bistro")
    page.locator(".login-container input[name='contrasena']").fill("12345")

    page.locator(".login-container button[type='submit']").click()
    page.wait_for_timeout(1500)


def ir_a_configuracion(page):
    """Función auxiliar para navegar a Configuración."""
    page.locator("#bmNav button[data-section='Configuración']").click()
    page.wait_for_timeout(1000)


def test_HU01_perfil_admin():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()

        print("\n========================================")
        print("   HU-01: Perfil Administrador")
        print("========================================")

        # Login inicial
        login(page)
        ir_a_configuracion(page)

        # =========================================================
        # CP-09: Editar correo administrador
        # =========================================================
        print("\n--- CP-09: Editar correo administrador ---")

        nuevo_correo = "bistro_nuevo@gmail.com"

        page.locator("[data-conf-edit-admin]").click()
        page.wait_for_timeout(800)

        page.locator(
            "[data-conf-admin-edit-form] input[name='correo']"
        ).fill(nuevo_correo)

        page.locator(
            "[data-conf-admin-edit-form] button[type='submit']"
        ).click()

        page.wait_for_timeout(1500)

        correo_visible = page.locator(
            "[data-conf-admin-correo]"
        ).inner_text()

        if nuevo_correo in correo_visible:
            print("[✅] CP-09 PASÓ: Correo actualizado correctamente")
        else:
            print(
                f"[❌] CP-09 FALLÓ: "
                f"Correo visible incorrecto -> {correo_visible}"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cp09_editar_correo_admin.png"
        )

        # Restaurar correo original
        page.locator("[data-conf-edit-admin]").click()
        page.wait_for_timeout(800)

        page.locator(
            "[data-conf-admin-edit-form] input[name='correo']"
        ).fill("bistro@gmail.com")

        page.locator(
            "[data-conf-admin-edit-form] button[type='submit']"
        ).click()

        page.wait_for_timeout(1000)

        # =========================================================
        # CP-10: Editar usuario administrador
        # =========================================================
        print("\n--- CP-10: Editar usuario administrador ---")

        nuevo_usuario = "bistro_nuevo"

        page.locator("[data-conf-edit-admin]").click()
        page.wait_for_timeout(800)

        page.locator(
            "[data-conf-admin-edit-form] input[name='usuario']"
        ).fill(nuevo_usuario)

        page.locator(
            "[data-conf-admin-edit-form] button[type='submit']"
        ).click()

        page.wait_for_timeout(1500)

        usuario_visible = page.locator(
            "[data-conf-admin-usuario]"
        ).inner_text()

        if nuevo_usuario in usuario_visible:
            print("[✅] CP-10 PASÓ: Usuario actualizado correctamente")
        else:
            print(
                f"[❌] CP-10 FALLÓ: "
                f"Usuario visible incorrecto -> {usuario_visible}"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cp10_editar_usuario_admin.png"
        )

        # Restaurar usuario original
        page.locator("[data-conf-edit-admin]").click()
        page.wait_for_timeout(800)

        page.locator(
            "[data-conf-admin-edit-form] input[name='usuario']"
        ).fill("bistro")

        page.locator(
            "[data-conf-admin-edit-form] button[type='submit']"
        ).click()

        page.wait_for_timeout(1000)

        # =========================================================
        # CP-11: Eliminar cuenta pide contraseña
        # =========================================================
        print("\n--- CP-11: Eliminar cuenta pide contraseña ---")

        page.locator("[data-conf-delete-account]").click()
        page.wait_for_timeout(1000)

        formulario_delete = page.locator(
            "[data-conf-view='admin_delete']"
        )

        campo_password = page.locator(
            "[data-conf-view='admin_delete'] input[type='password']"
        )

        if formulario_delete.is_visible() and campo_password.is_visible():
            print(
                "[✅] CP-11 PASÓ: "
                "Formulario de eliminación solicita contraseña"
            )
        else:
            print(
                "[❌] CP-11 FALLÓ: "
                "No apareció el formulario o falta el campo contraseña"
            )

        page.screenshot(
            path="frontend/tests/evidencias/cp11_eliminar_cuenta_password.png"
        )

        # Cancelar eliminación para no borrar la cuenta
        page.locator(
            "[data-conf-view='admin_delete'] [data-conf-cancel]"
        ).click()

        page.wait_for_timeout(800)

        browser.close()

        print("\n========================================")
        print("   HU-01: 3 casos ejecutados")
        print("========================================\n")


if __name__ == "__main__":
    test_HU01_perfil_admin()