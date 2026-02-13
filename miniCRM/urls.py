"""
URL configuration for miniCRM project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from clientes import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    # Clientes
    path('', views.lista_clientes, name='lista_clientes'),
    path('nuevo/', views.nuevo_cliente, name='nuevo_cliente'),
    path('editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
    path('eliminar/<int:id>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('cliente/<int:id>/', views.detalles_cliente, name='detalles_cliente'),

    # Contactos
    path('cliente/<int:cliente_id>/contacto/nuevo/', views.nuevo_contacto, name='nuevo_contacto'),
    path('contacto/<int:contacto_id>/editar/', views.editar_contacto, name='editar_contacto'),
    path('contacto/<int:contacto_id>/eliminar/', views.eliminar_contacto, name='eliminar_contacto'),

    # Actividades
    path('cliente/<int:cliente_id>/actividad/nueva/', views.nueva_actividad, name='nueva_actividad'),
    path('actividad/<int:actividad_id>/editar/', views.editar_actividad, name='editar_actividad'),
    path('actividad/<int:actividad_id>/eliminar/', views.eliminar_actividad, name='eliminar_actividad'),

    # Login
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
