from django.urls import path
from .views import AI_Assistance_List_View, FitnessPlanListView, FitnessPlanDateDetailView

urlpatterns = [
    path('ai-assistance/', AI_Assistance_List_View.as_view(), name='generate-plan'),
    path('fitness-plans/', FitnessPlanListView.as_view(), name='list-plans'),
    path('fitness-plans/<int:plan_id>/<str:target_date>/', FitnessPlanDateDetailView.as_view(), name='plan-date-detail'),

]
