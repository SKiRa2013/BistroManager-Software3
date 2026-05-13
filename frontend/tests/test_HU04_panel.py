from playwright.sync_api import sync_playwright


def login(page):
    page.goto("http://127.0.0.1:8000/admin/")
    page.wait_for_selector(".login-container")
    page.locator("input[name='usuario']").fill("bistro")
    page.locator("input[name='contrasena']").fill("12345")
    page.locator("button[type='submit']").click()
    page.wait_for_timeout(2000)


def test_HU04_panel():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=700)
        page = browser.new_page()

        print("\n========================================")
        print("   HU-04 / Panel: Estado Restaurante y Navegación")
        print("========================================")

        login(page)

        # =====================================================
        # CP-F27: Cambiar restaurante a Cerrado
        # =====================================================
        print("\n--- CP-F27: Toggle restaurante a Cerrado ---")
        page.locator("#bmNav button[data-section='Configuración']").click()
        page.wait_for_timeout(1500)

        page.locator("[data-conf-edit-restaurant]").click()
        page.wait_for_timeout(1000)
        page.locator("[data-conf-restaurant-form] select[name='estado']").select_option("closed")
        page.locator("[data-conf-restaurant-form] button.bm-btn-primary").click()
        page.wait_for_timeout(1500)

        badge = page.locator("[data-conf-restaurant-badge]")
        texto = badge.inner_text()
        if texto == "Cerrado":
            print("[✅] CP-F27 PASÓ: Badge cambió a 'Cerrado'")
        else:
            print(f"[❌] CP-F27 FALLÓ: Badge muestra '{texto}'")
        page.screenshot(path="frontend/tests/evidencias/cpf27_restaurante_cerrado.png")

        # =====================================================
        # CP-F28: Cambiar restaurante a Abierto
        # =====================================================
        print("\n--- CP-F28: Toggle restaurante a Abierto ---")
        page.locator("[data-conf-edit-restaurant]").click()
        page.wait_for_timeout(1000)
        page.locator("[data-conf-restaurant-form] select[name='estado']").select_option("open")
        page.locator("[data-conf-restaurant-form] button.bm-btn-primary").click()
        page.wait_for_timeout(1500)

        badge2 = page.locator("[data-conf-restaurant-badge]")
        texto2 = badge2.inner_text()
        if texto2 == "Abierto":
            print("[✅] CP-F28 PASÓ: Badge volvió a 'Abierto'")
        else:
            print(f"[❌] CP-F28 FALLÓ: Badge muestra '{texto2}'")
        page.screenshot(path="frontend/tests/evidencias/cpf28_restaurante_abierto.png")

        # =====================================================
        # CP-F29: Navegación sidebar lineal completa
        # =====================================================
        print("\n--- CP-F29: Navegación sidebar ---")
        secciones = [
            "Pedidos",
            "Tiqueteras",
            "Domicilios",
            "Usuarios",
            "Meseros",
            "Domiciliarios",
            "Inventario",
            "Configuración"
        ]
        todas_ok = True

        for seccion in secciones:
            page.locator(f"#bmNav button[data-section='{seccion}']").click()
            page.wait_for_timeout(1200)
            titulo = page.locator("#bmSectionTitle").inner_text()
            if titulo == seccion:
                print(f"  [✅] '{seccion}' cargó correctamente")
            else:
                print(f"  [❌] '{seccion}' falló, título muestra '{titulo}'")
                todas_ok = False
            page.screenshot(path=f"frontend/tests/evidencias/cpf29_nav_{seccion.lower()}.png")

        if todas_ok:
            print("[✅] CP-F29 PASÓ: Navegación sidebar funciona correctamente")
        else:
            print("[❌] CP-F29 FALLÓ: Alguna sección no cargó bien")

        # =====================================================
        # CP-F30: Botón Agregar visible por sección
        # (continúa desde Configuración, va solo a las que tienen botón)
        # =====================================================
        print("\n--- CP-F30: Botón Agregar visible por sección ---")
        todas_ok = True

        secciones_con_boton = ["Meseros", "Domiciliarios", "Configuración"]

        for seccion in secciones_con_boton:
            page.locator(f"#bmNav button[data-section='{seccion}']").click()
            page.wait_for_timeout(1000)
            boton = page.locator("button#bmPrimaryAction")
            if not boton.is_hidden():
                print(f"  [✅] '{seccion}' tiene botón Agregar visible")
            else:
                print(f"  [❌] '{seccion}' debería tener botón Agregar pero está oculto")
                todas_ok = False

        if todas_ok:
            print("[✅] CP-F30 PASÓ: Botón Agregar visible en secciones correctas")
        else:
            print("[❌] CP-F30 FALLÓ: Alguna sección no tiene el botón")
        page.screenshot(path="frontend/tests/evidencias/cpf30_boton_agregar.png")

        # =====================================================
        # CP-F31: Menú de usuario
        # =====================================================
        print("\n--- CP-F31: Menú de usuario ---")
        page.locator("#bmUserBtn").click()
        page.wait_for_timeout(1000)

        menu = page.locator("#bmUserMenu")
        if menu.get_attribute("aria-hidden") == "false":
            print("[✅] Menú se abrió al hacer clic")
        else:
            print("[❌] Menú no se abrió")

        page.screenshot(path="frontend/tests/evidencias/cpf31_menu_usuario.png")

        page.locator("#bmUserBtn").click()
        page.wait_for_timeout(1000)

        if menu.get_attribute("aria-hidden") == "true":
            print("[✅] CP-F31 PASÓ: Menú se cierra con segundo clic")
        else:
            print("[❌] CP-F31 FALLÓ: Menú no se cerró")

        browser.close()
        print("\n========================================")
        print("   HU-04/Panel: 5 casos ejecutados")
        print("========================================\n")


if __name__ == "__main__":
    test_HU04_panel()