from django.contrib import admin
from .models import Cliente, Contacto

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'empresa')
    search_fields = ('nombre', 'email', 'empresa')
    list_filter = ('empresa',)

@admin.register(Contacto)
class ContactoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'telefono', 'cliente')
    search_fields = ('nombre', 'email')
    list_filter = ('cliente',)
