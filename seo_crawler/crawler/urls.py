from django.urls import path
from .views import DomainListView, PageListView, InsightDetailView

urlpatterns = [
    path("domains/", DomainListView.as_view(), name="domain-list"),
    path("domains/<int:domain_id>/pages/", PageListView.as_view(), name="page-list"),
    path("pages/<int:pk>/insights/", InsightDetailView.as_view(), name="insight-detail"),
]
