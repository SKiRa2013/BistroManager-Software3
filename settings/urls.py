"""
URL configuration for settings project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from apps.BistroMaster import views as bistromaster_views

urlpatterns = [
    path('api/auth/login/', bistromaster_views.api_login, name='api_login'),
    path('admin/', bistromaster_views.login_admin, name='admin_login'),
    path('admin/forgot/', bistromaster_views.admin_forgot_password, name='admin_forgot'),
    path('admin/panel/', bistromaster_views.panel_admin, name='admin_panel'),
    path('admin/logout/', bistromaster_views.logout_admin, name='admin_logout'),
    path('admin/meseros/', bistromaster_views.meseros_api, name='meseros_api'),
    path('admin/meseros/<int:mesero_id>/', bistromaster_views.mesero_api, name='mesero_api'),
    path('admin/domiciliarios/', bistromaster_views.domiciliarios_api, name='domiciliarios_api'),
    path('admin/domiciliarios/<int:domiciliario_id>/', bistromaster_views.domiciliario_api, name='domiciliario_api'),
    path('admin/configuracion/', bistromaster_views.configuracion_api, name='configuracion_api'),
    path('admin/admin/profile/', bistromaster_views.admin_profile_api, name='admin_profile_api'),
    path('admin/admins/send-code/', bistromaster_views.admin_send_code_api, name='admin_send_code_api'),
    path('admin/admins/create/', bistromaster_views.admin_create_api, name='admin_create_api'),
    path('admin/restaurante/', bistromaster_views.restaurante_config_api, name='restaurante_config_api'),
    path('admin/admin/delete/', bistromaster_views.admin_delete_api, name='admin_delete_api'),
    path('admin/pedidos/lista/', bistromaster_views.pedidos_lista_api, name='pedidos_lista_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
