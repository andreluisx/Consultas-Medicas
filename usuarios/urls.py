
from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('sair/', views.sair, name="sair"),
]
