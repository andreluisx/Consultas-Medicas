from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'analise'

urlpatterns = [
    path('', views.analise, name='analise'),
    path('aprovados/', views.aprovados, name='aprovados'),
    path('reprovados/', views.reprovados, name='reprovados'),
    path('perfil-medico/<int:id>', views.perfil_medico, name='perfil-medico'),
    path('atualizar-status/<int:id>', views.atualizar_status, name='atualizar-status'),
     path('acesso-negado/', TemplateView.as_view(template_name='acesso_negado.html'), name='acesso_negado'),
]
