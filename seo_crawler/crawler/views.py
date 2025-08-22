from rest_framework import generics
from .models import Domain, Page, Insight
from .serializers import DomainSerializer, PageSerializer, InsightSerializer
from .pagination import CustomPageNumberPagination

class DomainListView(generics.ListAPIView):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer


class PageListView(generics.ListAPIView):
    serializer_class = PageSerializer
    pagination_class = CustomPageNumberPagination
    
    def get_queryset(self):
        domain_id = self.kwargs["domain_id"]
        return Page.objects.filter(domain_id=domain_id)


class InsightDetailView(generics.RetrieveAPIView):
    queryset = Insight.objects.all()
    serializer_class = InsightSerializer

