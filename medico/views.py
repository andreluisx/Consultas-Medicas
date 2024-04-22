from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Especialidades, DadosMedico
from .models import*
from django.contrib import messages
from django.contrib.messages import constants
from datetime import datetime, timedelta
from paciente.models import Consulta
from paciente.models import Documento
# Create your views here.

@login_required
def cadastro_medico(request):

    dm = DadosMedico.objects.filter(user=request.user).first()
    if dm is not None:
        if dm.status == 'aprovado':
            messages.add_message(request, constants.WARNING, 'Você ja é Médico')
            return redirect('/medico/home')
        elif dm.status == 'negado':
            messages.add_message(request, constants.WARNING, 'Seu cadastro médico foi negado')
            return redirect('/medicos/cadastro_medico')
        elif dm.status == 'analise':
            messages.add_message(request, constants.WARNING, 'Seu cadastro médico esta em analise')
            return redirect('/pacientes/home')

    if request.method == "GET":
        especialidades = Especialidades.objects.all()
        return render(request, 'cadastro_medico.html', {'especialidades': especialidades})
    elif request.method == "POST":
        crm = request.POST.get('crm')
        nome = request.POST.get('nome')
        cep = request.POST.get('cep')
        rua = request.POST.get('rua')
        bairro = request.POST.get('bairro')
        numero = request.POST.get('numero')
        cim = request.FILES.get('cim')
        rg = request.FILES.get('rg')
        foto = request.FILES.get('foto')
        especialidade = request.POST.get('especialidade')
        descricao = request.POST.get('descricao')
        valor_consulta = request.POST.get('valor_consulta')

        #TODO: Validar todos os campos

        dados_medico = DadosMedico(
            crm=crm,
            nome=nome,
            cep=cep,
            rua=rua,
            bairro=bairro,
            numero=numero,
            rg=rg,
            cedula_identidade_medica=cim,
            foto=foto,
            user=request.user,
            descricao=descricao,
            especialidade_id=especialidade,
            valor_consulta=valor_consulta
        )
        dados_medico.save()

        messages.add_message(request, constants.SUCCESS, 'Cadastro médico realizado com sucesso.')

        return redirect('/pacientes/home')
    
@login_required
def abrir_horario(request):
    dados_medicos = DadosMedico.objects.get(user=request.user)
    horarios = DatasAbertas.objects.filter(user=request.user)
    if dados_medicos == None or dados_medicos.status != 'aprovado':
        messages.add_message(request, constants.WARNING, 'Somente medicos podem abrir horarios')
        return redirect('/pacientes/home')

    if request.method == "GET":
        return render(request, 'abrir_horario.html', {'dados_medicos': dados_medicos, 'horarios': horarios})
    elif request.method == 'POST':
        data = request.POST.get('data')
        data_formatada = datetime.strptime(data, "%Y-%m-%dT%H:%M")
        if data_formatada <= datetime.now():
            messages.add_message(request, constants.ERROR, 'A data não pode ser menor que a data atual')
            return redirect('/medicos/abrir_horario')
        
        horario_abrir = DatasAbertas(data=data_formatada, user=request.user)

        horario_abrir.save()
        messages.add_message(request, constants.SUCCESS, 'Cadastro realizado com sucesso')
        return redirect('/medicos/abrir_horario')

@login_required
def consultas_medico(request):
    dados_medicos = DadosMedico.objects.get(user=request.user)
    if dados_medicos == None or dados_medicos.status != 'aprovado':
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    hoje = datetime.now().date()

    consultas_hoje = Consulta.objects.filter(data_aberta__user=request.user).filter(data_aberta__data__gte=hoje).filter(data_aberta__data__lt=hoje + timedelta(days=1))
    consultas_restantes = Consulta.objects.exclude(id__in=consultas_hoje.values('id')).filter(data_aberta__user=request.user)

    return render(request, 'consultas_medico.html', {'consultas_hoje': consultas_hoje, 'consultas_restantes': consultas_restantes, 'is_medico': request.user})

def consulta_area_medico(request, id_consulta):
    dados_medicos = DadosMedico.objects.get(user=request.user)
    if dados_medicos == None or dados_medicos.status != 'aprovado':
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    if request.method == "GET":
        consulta = Consulta.objects.get(id=id_consulta)
        documentos = Documento.objects.filter(consulta=consulta)
        return render(request, 'consulta_area_medico.html', {'consulta': consulta, 'documentos': documentos}) 
    
    elif request.method == "POST":
        # Inicializa a consulta + link da chamada
        consulta = Consulta.objects.get(id=id_consulta)
        link = request.POST.get('link')

        if consulta.status == 'C':
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi cancelada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        elif consulta.status == "F":
            messages.add_message(request, constants.WARNING, 'Essa consulta já foi finalizada, você não pode inicia-la')
            return redirect(f'/medicos/consulta_area_medico/{id_consulta}')
        
        consulta.link = link
        consulta.status = 'I'
        consulta.save()
        
        messages.add_message(request, constants.SUCCESS, 'Consulta inicializada com sucesso.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

def finalizar_consulta(request, id_consulta):
    dados_medicos = DadosMedico.objects.get(user=request.user)
    if dados_medicos == None or dados_medicos.status != 'aprovado':
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    if request.user != consulta.data_aberta.user:
        messages.add_message(request, constants.WARNING, 'Essa consulta não é sua.')
        return redirect(f'/medicos/consulta_area_medicos/{id_consulta}')
    
def add_documento(request, id_consulta):
    dados_medicos = DadosMedico.objects.get(user=request.user)
    if dados_medicos == None or dados_medicos.status != 'aprovado':
        messages.add_message(request, constants.WARNING, 'Somente médicos podem acessar essa página.')
        return redirect('/usuarios/sair')
    
    consulta = Consulta.objects.get(id=id_consulta)
    
    if consulta.data_aberta.user != request.user:
        messages.add_message(request, constants.ERROR, 'Essa consulta não é sua!')
        return redirect(f'/medicos/abrir_horario')
    
    
    titulo = request.POST.get('titulo')
    documento = request.FILES.get('documento')

    if not documento:
        messages.add_message(request, constants.WARNING, 'Adicione o documento.')
        return redirect(f'/medicos/consulta_area_medico/{id_consulta}')

    documento = Documento(
        consulta=consulta,
        titulo=titulo,
        documento=documento

    )

    documento.save()

    messages.add_message(request, constants.SUCCESS, 'Documento enviado com sucesso!')
    return redirect(f'/medicos/consulta_area_medico/{id_consulta}')