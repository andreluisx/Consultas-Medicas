from django.shortcuts import render, get_object_or_404, redirect
from medico.models import DadosMedico
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

def admin_required(view_func):
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='/pacientes/home/',
    )
    return actual_decorator(view_func)

@admin_required
def analise(request):
    title = 'Em Análise'
    medicos = DadosMedico.objects.filter(status='analise')
    return render(request, 'lista_medicos.html', {'medicos': medicos, 'title': title})

@admin_required
def perfil_medico(request, id):
    medico = get_object_or_404(DadosMedico, pk=id)
    return render(request, 'perfil_medico.html', {'medico': medico})

@admin_required
def atualizar_status(request, id):
    medico = get_object_or_404(DadosMedico, pk=id)
    if request.method == "GET":
        return render(request, 'perfil_medico.html', {'medico': medico})
    elif request.method == "POST":
        new_status = request.POST.get('status')
        medico.status = new_status
        medico.save()

        messages.add_message(request, constants.SUCCESS, 'Status alterado com sucesso.')
        return redirect(f'/analise/perfil-medico/{id}')

@admin_required         
def aprovados(request):
    title = 'Aprovados'
    medicos = DadosMedico.objects.filter(status='aprovado')
    return render(request, 'lista_medicos.html', {'medicos': medicos, 'title': title})

@admin_required
def reprovados(request):
    title = 'Negados'
    medicos = DadosMedico.objects.filter(status='negado')
    return render(request, 'lista_medicos.html', {'medicos': medicos, 'title': title})
    
