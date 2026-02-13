from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Contacto, Actividad
from django.contrib import messages  # añadido

# Para la búsqueda
from django.core.paginator import Paginator
from django.db.models import Q

from django.contrib.auth.decorators import login_required

# Create your views here.

# Ver lista de clientes
@login_required
def lista_clientes(request):
    # Clientes del usuario logueado
    clientes_queryset = Cliente.objects.filter(usuario=request.user)

    # Búsqueda
    raw_q = request.GET.get('q', '')
    query = raw_q.strip() if raw_q and raw_q.lower() != 'none' else ''

    if query:
        clientes_queryset = clientes_queryset.filter(
            Q(nombre__icontains=query) | Q(email__icontains=query)
        )

    # Paginación
    paginator = Paginator(clientes_queryset, 10)  # 10 clientes por página
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)

    return render(request, 'clientes/lista.html', {
        'clientes': clientes,
        'query': query,
    })

# Crear nuevo cliente
@login_required
def nuevo_cliente(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        telefono = request.POST['telefono']
        email = request.POST['email']
        empresa = request.POST['empresa']
        notas = request.POST['notas']
        
        # Asignar correctamente el usuario
        Cliente.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
            empresa=empresa,
            notas=notas,
            usuario=request.user
        )
        return redirect('lista_clientes')
    return render(request, 'clientes/nuevo.html')

# Editar cliente
@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id, usuario=request.user)
    if request.method == 'POST':
        cliente.nombre = request.POST['nombre']
        cliente.telefono = request.POST['telefono']
        cliente.email = request.POST['email']
        cliente.empresa = request.POST['empresa']
        cliente.notas = request.POST['notas']
        cliente.save()
        return redirect('lista_clientes')
    return render(request, 'clientes/editar.html', {'cliente': cliente})

# Eliminar cliente
@login_required
def eliminar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id, usuario=request.user)
    cliente.delete()
    messages.success(request, f"El cliente '{cliente.nombre}' ha sido eliminado correctamente.")
    return redirect('lista_clientes')


# crear contactos
@login_required
def nuevo_contacto(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario=request.user)

    if request.method == 'POST':
        Contacto.objects.create(
            cliente=cliente,
            nombre=request.POST['nombre'],
            email=request.POST.get('email', ''),
            telefono=request.POST.get('telefono', ''),
            cargo=request.POST.get('cargo', ''),
            notas=request.POST.get('notas', '')
        )
        messages.success(request, 'Contacto añadido correctamente')
        return redirect('detalles_cliente', id=cliente.id)

    return render(request, 'clientes/nuevo_contacto.html', {
        'cliente': cliente
    })


# ver información del cliente
@login_required
def detalles_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id, usuario=request.user)
    contactos = cliente.contactos.all()  # related_name
    actividades = cliente.actividades.order_by('-fecha')

    return render(request, 'clientes/detalles_cliente.html', {
        'cliente': cliente,
        'contactos': contactos,
        'actividades': actividades,
    })


# edicion pero de contacto
@login_required
def editar_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)
    cliente = contacto.cliente  # relación

    if request.method == "POST":
        contacto.nombre = request.POST.get("nombre")
        contacto.email = request.POST.get("email")
        contacto.telefono = request.POST.get("telefono")
        contacto.cargo = request.POST.get("cargo")
        contacto.notas = request.POST.get("notas")
        contacto.save()

        return redirect("detalles_cliente", cliente.id)

    return render(request, "clientes/editar_contacto.html", {
        "contacto": contacto,
        "cliente": cliente
    })


# eliminacion contacto
@login_required
def eliminar_contacto(request, contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)
    cliente = contacto.cliente  # guarda el cliente
    contacto.delete()
    messages.success(request, f"El contacto '{contacto.nombre}' ha sido eliminado correctamente.")  # Mensaje
    return redirect('detalles_cliente', cliente.id)  # devuelve a detalles


# actividades, nueva actividad
@login_required
def nueva_actividad(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id, usuario=request.user)

    if request.method == 'POST':
        tipo = request.POST['tipo']
        descripcion = request.POST['descripcion']

        Actividad.objects.create(
            cliente=cliente,
            tipo=tipo,
            descripcion=descripcion
        )

        messages.success(request, 'Actividad registrada correctamente')
        return redirect('detalles_cliente', cliente.id)

    return render(request, 'clientes/nueva_actividad.html', {
        'cliente': cliente
    })


@login_required
def editar_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    cliente = actividad.cliente

    if request.method == 'POST':
        actividad.tipo = request.POST['tipo']
        actividad.descripcion = request.POST['descripcion']
        actividad.save()
        messages.success(request, 'Actividad actualizada correctamente')
        return redirect('detalles_cliente', cliente.id)

    return render(request, 'clientes/editar_actividad.html', {
        'actividad': actividad,
        'cliente': cliente
    })


@login_required
def eliminar_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    cliente_id = actividad.cliente.id
    actividad.delete()
    messages.success(request, 'Actividad eliminada correctamente')
    return redirect('detalles_cliente', cliente_id)
