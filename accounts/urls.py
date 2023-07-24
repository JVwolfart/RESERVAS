from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('logout/', views.logout, name='logout'),
    path('lista_usuarios/', views.lista_usuarios, name='lista_usuarios'),
]