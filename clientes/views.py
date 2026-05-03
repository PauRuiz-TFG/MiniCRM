from django.shortcuts import render, redirect, get_object_or_404
from .models import Cliente, Contacto, Actividad
from django.contrib import messages  # añadido

# Para la búsqueda
from django.core.paginator import Paginator
from django.db.models import Q, Count

from django.contrib.auth.decorators import login_required

from django.utils import timezone
import json

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
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        notas = request.POST.get('notas', '').strip()

        # VALIDACIONES
        if not nombre:
            messages.error(request, "El nombre es obligatorio")
            return render(request, 'clientes/nuevo.html')

        if email and '@' not in email:
            messages.error(request, "El email no es válido")
            return render(request, 'clientes/nuevo.html')

        # CREACIÓN
        Cliente.objects.create(
            nombre=nombre,
            telefono=telefono,
            email=email,
            empresa=empresa,
            notas=notas,
            usuario=request.user
        )

        messages.success(request, "Cliente creado correctamente")
        return redirect('lista_clientes')

    return render(request, 'clientes/nuevo.html')


# Editar cliente
@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id, usuario=request.user)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email = request.POST.get('email', '').strip()
        empresa = request.POST.get('empresa', '').strip()
        notas = request.POST.get('notas', '').strip()

        # VALIDACIONES
        if not nombre:
            messages.error(request, "El nombre es obligatorio")
            return render(request, 'clientes/editar.html', {'cliente': cliente})

        if email and '@' not in email:
            messages.error(request, "El email no es válido")
            return render(request, 'clientes/editar.html', {'cliente': cliente})

        # GUARDAR
        cliente.nombre = nombre
        cliente.telefono = telefono
        cliente.email = email
        cliente.empresa = empresa
        cliente.notas = notas
        cliente.save()

        messages.success(request, "Cliente actualizado correctamente")
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
        nombre = request.POST.get('nombre', '').strip()
        email = request.POST.get('email', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        cargo = request.POST.get('cargo', '').strip()
        notas = request.POST.get('notas', '').strip()

        # VALIDACIONES
        if not nombre:
            messages.error(request, "El nombre del contacto es obligatorio")
            return render(request, 'clientes/nuevo_contacto.html', {'cliente': cliente})

        if email and '@' not in email:
            messages.error(request, "El email no es válido")
            return render(request, 'clientes/nuevo_contacto.html', {'cliente': cliente})

        # CREACIÓN
        Contacto.objects.create(
            cliente=cliente,
            nombre=nombre,
            email=email,
            telefono=telefono,
            cargo=cargo,
            notas=notas
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


# edición de contacto
@login_required
def editar_contacto(request, contacto_id):
    contacto = get_object_or_404(
        Contacto, 
        id=contacto_id, 
        cliente__usuario=request.user
    )
    cliente = contacto.cliente

    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        email = request.POST.get("email", "").strip()
        telefono = request.POST.get("telefono", "").strip()
        cargo = request.POST.get("cargo", "").strip()
        notas = request.POST.get("notas", "").strip()

        # VALIDACIONES
        if not nombre:
            messages.error(request, "El nombre del contacto es obligatorio")
            return render(request, "clientes/editar_contacto.html", {
                "contacto": contacto,
                "cliente": cliente
            })

        if email and '@' not in email:
            messages.error(request, "El email no es válido")
            return render(request, "clientes/editar_contacto.html", {
                "contacto": contacto,
                "cliente": cliente
            })

        # GUARDAR
        contacto.nombre = nombre
        contacto.email = email
        contacto.telefono = telefono
        contacto.cargo = cargo
        contacto.notas = notas
        contacto.save()

        messages.success(request, "Contacto actualizado correctamente")
        return redirect("detalles_cliente", cliente.id)

    return render(request, "clientes/editar_contacto.html", {
        "contacto": contacto,
        "cliente": cliente
    })


# eliminación contacto
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
        tipo = request.POST.get('tipo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        # VALIDACIONES
        if not tipo:
            messages.error(request, "El tipo de actividad es obligatorio")
            return render(request, 'clientes/nueva_actividad.html', {
                'cliente': cliente
            })

        if not descripcion:
            messages.error(request, "La descripción es obligatoria")
            return render(request, 'clientes/nueva_actividad.html', {
                'cliente': cliente
            })

        # CREACIÓN
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
    actividad = get_object_or_404(
        Actividad, 
        id=actividad_id, 
        cliente__usuario=request.user
    )
    cliente = actividad.cliente

    if request.method == 'POST':
        tipo = request.POST.get('tipo', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()

        # VALIDACIONES
        if not tipo:
            messages.error(request, "El tipo de actividad es obligatorio")
            return render(request, 'clientes/editar_actividad.html', {
                'actividad': actividad,
                'cliente': cliente
            })

        if not descripcion:
            messages.error(request, "La descripción es obligatoria")
            return render(request, 'clientes/editar_actividad.html', {
                'actividad': actividad,
                'cliente': cliente
            })

        # GUARDAR
        actividad.tipo = tipo
        actividad.descripcion = descripcion
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


@login_required
def dashboard(request):
    total_clientes = Cliente.objects.filter(usuario=request.user).count()
    total_contactos = Contacto.objects.filter(cliente__usuario=request.user).count()
    total_actividades = Actividad.objects.filter(cliente__usuario=request.user).count()

    actividades_recientes = Actividad.objects.filter(
        cliente__usuario=request.user
    ).order_by('-fecha')[:25]

    actividades_por_tipo = Actividad.objects.filter(
        cliente__usuario=request.user
    ).values('tipo').annotate(total=Count('tipo')).order_by('tipo')

    labels_actividades = json.dumps([a['tipo'] for a in actividades_por_tipo])
    totales_actividades = json.dumps([a['total'] for a in actividades_por_tipo])

    return render(request, 'clientes/dashboard.html', {
        'total_clientes': total_clientes,
        'total_contactos': total_contactos,
        'total_actividades': total_actividades,
        'actividades_recientes': actividades_recientes,
        'labels_actividades': labels_actividades,
        'totales_actividades': totales_actividades,
    })


@login_required
def reporte_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id, usuario=request.user)
    contactos = cliente.contactos.all()
    actividades = cliente.actividades.order_by('-fecha')

    return render(request, 'clientes/reporte_cliente.html', {
        'cliente': cliente,
        'contactos': contactos,
        'actividades': actividades,
        'now': timezone.now(),
    })


@login_required
def reporte_global(request):
    total_clientes = Cliente.objects.filter(usuario=request.user).count()
    total_contactos = Contacto.objects.filter(cliente__usuario=request.user).count()
    total_actividades = Actividad.objects.filter(cliente__usuario=request.user).count()

    actividades_recientes = Actividad.objects.filter(
        cliente__usuario=request.user
    ).order_by('-fecha')[:20]

    actividades_por_tipo = Actividad.objects.filter(
        cliente__usuario=request.user
    ).values('tipo').annotate(total=Count('tipo'))

    return render(request, 'clientes/reporte_global.html', {
        'total_clientes': total_clientes,
        'total_contactos': total_contactos,
        'total_actividades': total_actividades,
        'actividades_recientes': actividades_recientes,
        'actividades_por_tipo': actividades_por_tipo,
        'now': timezone.now(),
    })
