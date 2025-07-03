# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('ghg/', views.ghg_insights, name='ghg_insights'),
    path('ghg-trend/', views.ghg_trend_view, name='ghg_trend'),
    path('co2-emission/', views.co2_emission_view, name='co2_emission'),
    path('co2-bio/', views.co2_bio_view, name='co2_bio'),
    path('total-co2/', views.total_co2_view, name='total_co2'),
    path('ch4/', views.ch4_emissions_view, name='ch4_emissions'),
    path('n2o/', views.n2o_emissions_view, name='n2o_emissions'),
    path('intro/', views.ghg_intro_view, name='ghg_intro'),
    path('sector-summary/', views.sector_summary_view, name='sector_summary'),
    path('sector/<str:gas>/', views.sector_gas_trend_view, name='sector_gas_trend'),
    path('sector-guide/', views.sector_guide_view, name='sector_guide'),
]
