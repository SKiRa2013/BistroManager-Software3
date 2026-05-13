from playwright.sync_api import sync_playwright

def test_HU01_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=800)
        page = browser.new_page()

        print("\n========================================")
        print("  HU-01: Autenticación de Administrador")
        print("========================================")

        # --- CP-01: Login exitoso ---
        print("\n--- CP-01: Login exitoso ---")
        page.goto("http://127.0.0.1:8000/admin/")
        page.wait_for_selector(".login-container")
        page.locator(".login-container input[name='usuario']").fill("bistro")
        page.locator(".login-container input[name='contrasena']").fill("12345")
        page.locator(".login-container button[type='submit']").click()
        page.wait_for_timeout(1500)
        if "panel" in page.url:
            print("[✅] CP-01 PASÓ: Login exitoso, redirigió al panel")
        else:
            print("[❌] CP-01 FALLÓ: No redirigió al panel")
        page.screenshot(path="frontend/tests/evidencias/cp01_login_exitoso.png")

        # --- CP-02: Contraseña incorrecta ---
        print("\n--- CP-02: Contraseña incorrecta ---")
        page.goto("http://127.0.0.1:8000/admin/logout/")
        page.wait_for_timeout(1000)
        page.goto("http://127.0.0.1:8000/admin/")
        page.wait_for_selector(".login-container")
        page.locator(".login-container input[name='usuario']").fill("bistro")
        page.locator(".login-container input[name='contrasena']").fill("0000")
        page.locator(".login-container button[type='submit']").click()
        page.wait_for_timeout(1500)
        mensaje = page.locator("p.mensaje").inner_text()
        if "incorrectos" in mensaje.lower():
            print(f"[✅] CP-02 PASÓ: Mostró mensaje '{mensaje}'")
        else:
            print(f"[❌] CP-02 FALLÓ: Mensaje inesperado '{mensaje}'")
        page.screenshot(path="frontend/tests/evidencias/cp02_contrasena_incorrecta.png")

        # --- CP-03: Usuario inexistente ---
        print("\n--- CP-03: Usuario inexistente ---")
        page.locator(".login-container input[name='usuario']").fill("fake")
        page.locator(".login-container input[name='contrasena']").fill("1234")
        page.locator(".login-container button[type='submit']").click()
        page.wait_for_timeout(1500)
        mensaje = page.locator("p.mensaje").inner_text()
        if "incorrectos" in mensaje.lower():
            print(f"[✅] CP-03 PASÓ: Mostró mensaje '{mensaje}'")
        else:
            print(f"[❌] CP-03 FALLÓ: Mensaje inesperado '{mensaje}'")
        page.screenshot(path="frontend/tests/evidencias/cp03_usuario_inexistente.png")

        # --- CP-04: Campos vacíos ---
        print("\n--- CP-04: Campos vacíos ---")
        page.locator(".login-container input[name='usuario']").fill("")
        page.locator(".login-container input[name='contrasena']").fill("")
        page.locator(".login-container button[type='submit']").click()
        page.wait_for_timeout(1000)
        if "/admin/" in page.url and "panel" not in page.url:
            print("[✅] CP-04 PASÓ: Formulario bloqueó envío con campos vacíos")
        else:
            print("[❌] CP-04 FALLÓ: El formulario se envió sin validar")
        page.screenshot(path="frontend/tests/evidencias/cp04_campos_vacios.png")

        # --- CP-05: Espacios en blanco ---
        print("\n--- CP-05: Espacios en blanco ---")
        page.locator(".login-container input[name='usuario']").fill("   ")
        page.locator(".login-container input[name='contrasena']").fill("   ")
        page.locator(".login-container button[type='submit']").click()
        page.wait_for_timeout(1500)
        if "/admin/" in page.url and "panel" not in page.url:
            print("[✅] CP-05 PASÓ: Espacios en blanco no permiten acceso")
        else:
            print("[❌] CP-05 FALLÓ: Espacios en blanco permitieron acceso")
        page.screenshot(path="frontend/tests/evidencias/cp05_espacios_blanco.png")

        # --- CP-06: Acceso directo sin autenticación ---
        print("\n--- CP-06: Acceso directo sin autenticación ---")
        page.goto("http://127.0.0.1:8000/admin/logout/")
        page.wait_for_timeout(1000)
        page.goto("http://127.0.0.1:8000/admin/panel/")
        page.wait_for_timeout(1500)
        if "panel" not in page.url:
            print("[✅] CP-06 PASÓ: Sin auth redirige al login")
        else:
            print("[❌] CP-06 FALLÓ: Permitió acceso al panel sin autenticación")
        page.screenshot(path="frontend/tests/evidencias/cp06_acceso_sin_auth.png")

        # --- CP-07: Link ¿Olvidaste tu contraseña? ---
        print("\n--- CP-07: Link ¿Olvidaste tu contraseña? ---")
        page.goto("http://127.0.0.1:8000/admin/")
        page.wait_for_selector(".login-container")
        page.locator("a.bm-forgot").click()
        page.wait_for_timeout(1500)
        if "forgot" in page.url or "recuperar" in page.url:
            print("[✅] CP-07 PASÓ: Link ¿Olvidaste contraseña? navega correctamente")
        else:
            print("[❌] CP-07 FALLÓ: Link no navegó a recuperar contraseña")
        page.screenshot(path="frontend/tests/evidencias/cp07_link_olvide_contrasena.png")

        # --- CP-08: Volver al login desde recuperar contraseña ---
        print("\n--- CP-08: Volver al login desde recuperar contraseña ---")
        page.locator("a.bm-forgot").click()
        page.wait_for_timeout(1500)
        if "/admin/" in page.url and "forgot" not in page.url:
            print("[✅] CP-08 PASÓ: Volver al login funciona correctamente")
        else:
            print("[❌] CP-08 FALLÓ: No regresó al login")
        page.screenshot(path="frontend/tests/evidencias/cp08_volver_al_login.png")

        browser.close()

        print("\n========================================")
        print("  HU-01: 8 casos ejecutados")
        print("========================================\n")

if __name__ == "__main__":
    test_HU01_login()
