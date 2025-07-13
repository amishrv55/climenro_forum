from django.urls import path
from . import views

app_name = 'policy_graph'

urlpatterns = [
    path('add/', views.add_policy_view, name='add_policy'),
    path('graph/', views.graph_view, name='graph_view'),
    path('upload-policy/', views.upload_policy_pdf, name='upload_policy_pdf'),
]
