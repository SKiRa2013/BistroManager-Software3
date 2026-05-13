import json
import base64
import hashlib
import hmac
import random
import re
import time

from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from .models import Administrador, Domiciliario, Mesero, RestauranteConfig


def login_admin(request):
    if request.session.get("admin_id"):
        return redirect("admin_panel")

    mensaje = request.session.pop("login_flash", "")

    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasena = request.POST.get("contrasena")

        admin = Administrador.objects.filter(usuario=usuario).first()
        if admin:
            ok = False
            if check_password(contrasena or "", admin.contrasena):
                ok = True
            elif (admin.contrasena or "") == (contrasena or ""):
                ok = True
                admin.contrasena = make_password(contrasena or "")
                admin.save(update_fields=["contrasena"])

            if ok:
                request.session["admin_id"] = admin.id
                return redirect("admin_panel")

        mensaje = "Usuario o contraseña incorrectos"

    return render(request, "BistroMaster/login_admin.html", {"mensaje": mensaje})


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    usuario = (payload.get("usuario") or payload.get("username") or "").strip()
    contrasena = payload.get("contrasena") or payload.get("password") or ""

    if not usuario or not contrasena:
        return JsonResponse({"ok": False, "error": "Faltan credenciales"}, status=400)

    admin = Administrador.objects.filter(usuario=usuario).first()
    if not admin:
        return JsonResponse({"ok": False, "error": "Credenciales incorrectas"}, status=401)

    ok = False
    if check_password(contrasena, admin.contrasena):
        ok = True
    elif (admin.contrasena or "") == contrasena:
        ok = True
        admin.contrasena = make_password(contrasena)
        admin.save(update_fields=["contrasena"])

    if not ok:
        return JsonResponse({"ok": False, "error": "Credenciales incorrectas"}, status=401)

    now = int(time.time())
    token = _jwt_encode(
        {
            "sub": str(admin.id),
            "usuario": admin.usuario,
            "iat": now,
            "exp": now + 60 * 60,
        }
    )

    return JsonResponse(
        {
            "ok": True,
            "token": token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "admin": {"id": admin.id, "usuario": admin.usuario, "correo": admin.correo or ""},
        }
    )


def logout_admin(request):
    request.session.pop("admin_id", None)
    return redirect("admin_login")


def _require_admin_session(request):
    return _get_admin_from_request(request) is not None


def _get_admin_from_request(request) -> Administrador | None:
    admin_id = request.session.get("admin_id")
    if admin_id:
        admin = Administrador.objects.filter(id=admin_id).first()
        if admin:
            return admin

    auth = request.headers.get("Authorization") or ""
    if auth.startswith("Bearer "):
        token = auth.removeprefix("Bearer ").strip()
        payload = _jwt_decode(token)
        if payload and payload.get("sub"):
            try:
                admin_id = int(payload["sub"])
            except (TypeError, ValueError):
                return None
            return Administrador.objects.filter(id=admin_id).first()

    return None


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_json(obj: dict) -> str:
    return _b64url(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))


def _jwt_encode(payload: dict) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    signing_input = (_b64url_json(header) + "." + _b64url_json(payload)).encode("utf-8")
    sig = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    return signing_input.decode("utf-8") + "." + _b64url(sig)


def _jwt_decode(token: str) -> dict | None:
    try:
        h, p, s = token.split(".", 2)
    except ValueError:
        return None

    signing_input = (h + "." + p).encode("utf-8")
    expected = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
    try:
        sig = base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
    except Exception:
        return None

    if not hmac.compare_digest(sig, expected):
        return None

    try:
        payload = json.loads(base64.urlsafe_b64decode(p + "=" * (-len(p) % 4)).decode("utf-8"))
    except Exception:
        return None

    exp = payload.get("exp")
    if isinstance(exp, int) and int(time.time()) > exp:
        return None

    return payload


def _password_strength_error(password: str) -> str | None:
    if not password or len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return "La contraseña debe tener al menos una mayúscula."
    if not re.search(r"[a-z]", password):
        return "La contraseña debe tener al menos una minúscula."
    if not re.search(r"\d", password):
        return "La contraseña debe tener al menos un número."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "La contraseña debe tener al menos un carácter especial."
    return None


def _get_restaurant_config() -> RestauranteConfig:
    obj = RestauranteConfig.objects.order_by("id").first()
    if obj:
        return obj
    return RestauranteConfig.objects.create(is_open=True)


@require_http_methods(["GET", "POST"])
def admin_forgot_password(request):
    stage = "request"
    mensaje = ""
    correo = ""

    reset = request.session.get("admin_password_reset") or {}
    verified = request.session.get("admin_password_reset_verified") or {}

    if verified.get("correo"):
        stage = "reset"
        correo = verified.get("correo") or ""
    elif reset.get("correo"):
        stage = "verify"
        correo = reset.get("correo") or ""

    if request.method == "POST":
        action = request.POST.get("action") or ""
        correo = (request.POST.get("correo") or "").strip()

        if action == "send_code":
            admin = Administrador.objects.filter(correo=correo).first()
            if not correo:
                mensaje = "Falta el correo."
            elif not admin:
                mensaje = "No existe un administrador con ese correo."
            else:
                code = "".join(str(random.randint(0, 9)) for _ in range(6))
                request.session["admin_password_reset"] = {
                    "correo": correo,
                    "code": code,
                    "ts": int(time.time()),
                }
                request.session.pop("admin_password_reset_verified", None)
                request.session.modified = True

                try:
                    send_mail(
                        subject="Código de recuperación - BistroMaster",
                        message=(
                            "Recibimos una solicitud para cambiar la contraseña.\n\n"
                            f"Tu código de verificación es: {code}\n\n"
                            "Si no fuiste tú, puedes ignorar este correo."
                        ),
                        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None)
                        or getattr(settings, "EMAIL_HOST_USER", None),
                        recipient_list=[correo],
                        fail_silently=False,
                    )
                    mensaje = "Código enviado. Revisa tu correo e ingrésalo abajo."
                    stage = "verify"
                except Exception as exc:
                    mensaje = (
                        f"No se pudo enviar el correo: {exc}"
                        if settings.DEBUG
                        else "No se pudo enviar el correo. Revisa la configuración de email."
                    )

        elif action == "verify_code":
            code = (request.POST.get("code") or "").strip()
            reset = request.session.get("admin_password_reset") or {}
            if not correo:
                mensaje = "Falta el correo."
                stage = "verify"
            elif not code:
                mensaje = "Te falta poner el código enviado."
                stage = "verify"
            elif reset.get("correo") != correo or reset.get("code") != code:
                mensaje = "Código incorrecto."
                stage = "verify"
            elif int(time.time()) - int(reset.get("ts") or 0) > 15 * 60:
                mensaje = "El código expiró. Vuelve a enviarlo."
                stage = "verify"
            else:
                request.session["admin_password_reset_verified"] = {
                    "correo": correo,
                    "ts": int(time.time()),
                }
                request.session.modified = True
                stage = "reset"

        elif action == "reset_password":
            verified = request.session.get("admin_password_reset_verified") or {}
            correo = (request.POST.get("correo") or "").strip()
            contrasena = request.POST.get("contrasena") or ""
            confirmar = request.POST.get("confirmar_contrasena") or ""

            if verified.get("correo") != correo:
                mensaje = "Primero verifica el código."
                stage = "verify"
            elif not contrasena:
                mensaje = "Falta la contraseña."
                stage = "reset"
            elif confirmar != contrasena:
                mensaje = "Las contraseñas no coinciden."
                stage = "reset"
            else:
                strength_error = _password_strength_error(contrasena)
                if strength_error:
                    mensaje = strength_error
                    stage = "reset"
                else:
                    admin = Administrador.objects.filter(correo=correo).first()
                    if not admin:
                        mensaje = "No existe un administrador con ese correo."
                        stage = "request"
                    else:
                        admin.contrasena = make_password(contrasena)
                        admin.save(update_fields=["contrasena"])
                        request.session.pop("admin_password_reset", None)
                        request.session.pop("admin_password_reset_verified", None)
                        request.session["login_flash"] = (
                            "Contraseña actualizada. Ya puedes iniciar sesión."
                        )
                        return redirect("admin_login")
        else:
            mensaje = "Acción inválida."

    return render(
        request,
        "BistroMaster/forgot_password.html",
        {"stage": stage, "mensaje": mensaje, "correo": correo},
    )


@ensure_csrf_cookie
def panel_admin(request):
    admin_id = request.session.get("admin_id")
    if not admin_id:
        return redirect("admin_login")

    admin = Administrador.objects.filter(id=admin_id).first()
    if not admin:
        request.session.pop("admin_id", None)
        return redirect("admin_login")

    return render(request, "BistroMaster/panel_admin.html", {"admin": admin})


@require_http_methods(["GET", "POST"])
def meseros_api(request):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method == "GET":
        data = [
            {
                "id": m.id,
                "nombre": m.nombre,
                "usuario": m.usuario,
                "contrato": m.tipo_contrato,
                "disponible": m.disponible,
            }
            for m in Mesero.objects.order_by("nombre")
        ]
        return JsonResponse({"ok": True, "meseros": data})

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    nombre = (payload.get("nombre") or "").strip()
    usuario = (payload.get("usuario") or "").strip()
    contrasena = payload.get("contrasena") or ""
    contrasena_confirm = payload.get("contrasena_confirm") or ""
    contrato = (payload.get("contrato") or "").strip()
    disponible = bool(payload.get("disponible"))

    if not nombre or not usuario or not contrasena or not contrato:
        return JsonResponse({"ok": False, "error": "Faltan campos"}, status=400)

    if contrasena_confirm != contrasena:
        return JsonResponse({"ok": False, "error": "Las contraseñas no coinciden"}, status=400)

    if Mesero.objects.filter(nombre=nombre).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un mesero con ese nombre"}, status=400)

    if Mesero.objects.filter(usuario=usuario).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un mesero con ese usuario"}, status=400)

    m = Mesero(nombre=nombre, usuario=usuario, tipo_contrato=contrato, disponible=disponible)
    m.contrasena = make_password(contrasena)
    m.save()
    return JsonResponse(
        {
            "ok": True,
            "mesero": {
                "id": m.id,
                "nombre": m.nombre,
                "usuario": m.usuario,
                "contrato": m.tipo_contrato,
                "disponible": m.disponible,
            },
        },
        status=201,
    )


@require_http_methods(["PUT", "DELETE"])
def mesero_api(request, mesero_id: int):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    m = Mesero.objects.filter(id=mesero_id).first()
    if not m:
        return JsonResponse({"ok": False, "error": "No encontrado"}, status=404)

    if request.method == "DELETE":
        m.delete()
        return JsonResponse({"ok": True})

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    nombre = (payload.get("nombre") or "").strip()
    usuario = (payload.get("usuario") or "").strip()
    contrasena = payload.get("contrasena") or ""
    contrasena_confirm = payload.get("contrasena_confirm") or ""
    contrato = (payload.get("contrato") or "").strip()
    disponible = bool(payload.get("disponible"))

    if not nombre or not usuario or not contrato:
        return JsonResponse({"ok": False, "error": "Faltan campos"}, status=400)

    if Mesero.objects.filter(nombre=nombre).exclude(id=m.id).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un mesero con ese nombre"}, status=400)

    if Mesero.objects.filter(usuario=usuario).exclude(id=m.id).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un mesero con ese usuario"}, status=400)

    m.nombre = nombre
    m.usuario = usuario
    m.tipo_contrato = contrato
    m.disponible = disponible
    if contrasena:
        if contrasena_confirm != contrasena:
            return JsonResponse(
                {"ok": False, "error": "Las contraseñas no coinciden"}, status=400
            )
        m.contrasena = make_password(contrasena)
    m.save()

    return JsonResponse(
        {
            "ok": True,
            "mesero": {
                "id": m.id,
                "nombre": m.nombre,
                "usuario": m.usuario,
                "contrato": m.tipo_contrato,
                "disponible": m.disponible,
            },
        }
    )


@require_http_methods(["GET", "POST"])
def domiciliarios_api(request):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    if request.method == "GET":
        data = [
            {
                "id": d.id,
                "nombre": d.nombre,
                "usuario": d.usuario,
                "contrato": d.tipo_contrato,
                "disponible": d.disponible,
            }
            for d in Domiciliario.objects.order_by("nombre")
        ]
        return JsonResponse({"ok": True, "domiciliarios": data})

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    nombre = (payload.get("nombre") or "").strip()
    usuario = (payload.get("usuario") or "").strip()
    contrasena = payload.get("contrasena") or ""
    contrasena_confirm = payload.get("contrasena_confirm") or ""
    contrato = (payload.get("contrato") or "").strip()
    disponible = bool(payload.get("disponible"))

    if not nombre or not usuario or not contrasena or not contrato:
        return JsonResponse({"ok": False, "error": "Faltan campos"}, status=400)

    if contrasena_confirm != contrasena:
        return JsonResponse({"ok": False, "error": "Las contraseñas no coinciden"}, status=400)

    if Domiciliario.objects.filter(nombre=nombre).exists():
        return JsonResponse(
            {"ok": False, "error": "Ya existe un domiciliario con ese nombre"}, status=400
        )

    if Domiciliario.objects.filter(usuario=usuario).exists():
        return JsonResponse(
            {"ok": False, "error": "Ya existe un domiciliario con ese usuario"}, status=400
        )

    d = Domiciliario(
        nombre=nombre, usuario=usuario, tipo_contrato=contrato, disponible=disponible
    )
    d.contrasena = make_password(contrasena)
    d.save()
    return JsonResponse(
        {
            "ok": True,
            "domiciliario": {
                "id": d.id,
                "nombre": d.nombre,
                "usuario": d.usuario,
                "contrato": d.tipo_contrato,
                "disponible": d.disponible,
            },
        },
        status=201,
    )


@require_http_methods(["PUT", "DELETE"])
def domiciliario_api(request, domiciliario_id: int):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    d = Domiciliario.objects.filter(id=domiciliario_id).first()
    if not d:
        return JsonResponse({"ok": False, "error": "No encontrado"}, status=404)

    if request.method == "DELETE":
        d.delete()
        return JsonResponse({"ok": True})

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    nombre = (payload.get("nombre") or "").strip()
    usuario = (payload.get("usuario") or "").strip()
    contrasena = payload.get("contrasena") or ""
    contrasena_confirm = payload.get("contrasena_confirm") or ""
    contrato = (payload.get("contrato") or "").strip()
    disponible = bool(payload.get("disponible"))

    if not nombre or not usuario or not contrato:
        return JsonResponse({"ok": False, "error": "Faltan campos"}, status=400)

    if Domiciliario.objects.filter(nombre=nombre).exclude(id=d.id).exists():
        return JsonResponse(
            {"ok": False, "error": "Ya existe un domiciliario con ese nombre"}, status=400
        )

    if Domiciliario.objects.filter(usuario=usuario).exclude(id=d.id).exists():
        return JsonResponse(
            {"ok": False, "error": "Ya existe un domiciliario con ese usuario"}, status=400
        )

    d.nombre = nombre
    d.usuario = usuario
    d.tipo_contrato = contrato
    d.disponible = disponible
    if contrasena:
        if contrasena_confirm != contrasena:
            return JsonResponse(
                {"ok": False, "error": "Las contraseñas no coinciden"}, status=400
            )
        d.contrasena = make_password(contrasena)
    d.save()

    return JsonResponse(
        {
            "ok": True,
            "domiciliario": {
                "id": d.id,
                "nombre": d.nombre,
                "usuario": d.usuario,
                "contrato": d.tipo_contrato,
                "disponible": d.disponible,
            },
        }
    )


@require_http_methods(["GET"])
def configuracion_api(request):
    admin = _get_admin_from_request(request)
    if not admin:
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    rc = _get_restaurant_config()
    return JsonResponse(
        {
            "ok": True,
            "admin": {"id": admin.id, "usuario": admin.usuario, "correo": admin.correo or ""},
            "restaurante": {"is_open": rc.is_open},
        }
    )


@require_http_methods(["PUT"])
def admin_profile_api(request):
    admin = _get_admin_from_request(request)
    if not admin:
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    correo = (payload.get("correo") or "").strip()
    usuario = (payload.get("usuario") or "").strip()
    contrasena = payload.get("contrasena") or ""
    contrasena_confirm = payload.get("contrasena_confirm") or ""

    if not correo or not usuario:
        return JsonResponse({"ok": False, "error": "Faltan campos"}, status=400)

    if Administrador.objects.filter(usuario=usuario).exclude(id=admin.id).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un admin con ese usuario"}, status=400)

    if Administrador.objects.filter(correo=correo).exclude(id=admin.id).exists():
        return JsonResponse({"ok": False, "error": "Ya existe un admin con ese correo"}, status=400)

    admin.usuario = usuario
    admin.correo = correo

    if contrasena:
        if contrasena_confirm != contrasena:
            return JsonResponse({"ok": False, "error": "Las contraseñas no coinciden"}, status=400)
        strength_error = _password_strength_error(contrasena)
        if strength_error:
            return JsonResponse({"ok": False, "error": strength_error}, status=400)
        admin.contrasena = make_password(contrasena)

    admin.save()
    return JsonResponse({"ok": True})


@require_http_methods(["POST"])
def admin_send_code_api(request):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    correo = (payload.get("correo") or "").strip()
    if not correo:
        return JsonResponse({"ok": False, "error": "Falta el correo"}, status=400)

    if Administrador.objects.filter(correo=correo).exists():
        return JsonResponse({"ok": False, "error": "Ese correo ya está en uso"}, status=400)

    code = "".join(str(random.randint(0, 9)) for _ in range(6))
    request.session["admin_email_verification"] = {"correo": correo, "code": code, "ts": int(time.time())}
    request.session.modified = True

    try:
        send_mail(
            subject="Código de verificación - BistroMaster",
            message=f"Tu código de verificación es: {code}",
            from_email=f'BistroMaster <{settings.EMAIL_HOST_USER}>',
            recipient_list=[correo],
            fail_silently=False,
        )

    except Exception as exc:
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    f"No se pudo enviar el correo: {exc}"
                    if settings.DEBUG
                    else "No se pudo enviar el correo (revisa la configuración de email en Django)."
                ),
            },
            status=500,
        )

    return JsonResponse({"ok": True})


@require_http_methods(["POST"])
def admin_create_api(request):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    correo = (payload.get("correo") or "").strip()
    code = (payload.get("code") or "").strip()
    usuario = (payload.get("usuario") or "").strip()
    contrasena = payload.get("contrasena") or ""
    contrasena_confirm = payload.get("contrasena_confirm") or ""

    if not correo:
        return JsonResponse({"ok": False, "error": "Falta el correo"}, status=400)
    if not code:
        return JsonResponse({"ok": False, "error": "Falta el código de verificación"}, status=400)
    if not usuario:
        return JsonResponse({"ok": False, "error": "Falta el nombre de usuario"}, status=400)
    if not contrasena:
        return JsonResponse({"ok": False, "error": "Falta la contraseña"}, status=400)

    if contrasena_confirm != contrasena:
        return JsonResponse({"ok": False, "error": "Las contraseñas no coinciden"}, status=400)

    strength_error = _password_strength_error(contrasena)
    if strength_error:
        return JsonResponse({"ok": False, "error": strength_error}, status=400)

    if Administrador.objects.filter(usuario=usuario).exists():
        return JsonResponse({"ok": False, "error": "Ese usuario ya está en uso"}, status=400)

    if Administrador.objects.filter(correo=correo).exists():
        return JsonResponse({"ok": False, "error": "Ese correo ya está en uso"}, status=400)

    session_data = request.session.get("admin_email_verification") or {}
    if session_data.get("correo") != correo or session_data.get("code") != code:
        return JsonResponse({"ok": False, "error": "Código inválido"}, status=400)

    if int(time.time()) - int(session_data.get("ts") or 0) > 15 * 60:
        return JsonResponse({"ok": False, "error": "El código expiró"}, status=400)

    new_admin = Administrador(usuario=usuario, correo=correo)
    new_admin.contrasena = make_password(contrasena)
    new_admin.save()

    return JsonResponse({"ok": True})


@require_http_methods(["PUT"])
def restaurante_config_api(request):
    if not _require_admin_session(request):
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    is_open = bool(payload.get("is_open"))
    rc = _get_restaurant_config()
    rc.is_open = is_open
    rc.save(update_fields=["is_open", "updated_at"])
    return JsonResponse({"ok": True, "restaurante": {"is_open": rc.is_open}})


@require_http_methods(["POST"])
def admin_delete_api(request):
    admin = _get_admin_from_request(request)
    if not admin:
        return JsonResponse({"ok": False, "error": "No autorizado"}, status=401)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)

    contrasena = payload.get("contrasena") or ""
    if not contrasena:
        return JsonResponse({"ok": False, "error": "Falta la contraseña"}, status=400)

    ok = False
    if check_password(contrasena, admin.contrasena):
        ok = True
    elif (admin.contrasena or "") == contrasena:
        ok = True

    if not ok:
        return JsonResponse({"ok": False, "error": "Contraseña incorrecta"}, status=400)

    admin.delete()
    request.session.pop("admin_id", None)
    request.session.pop("admin_email_verification", None)
    return JsonResponse({"ok": True, "redirect": "/admin/"})
