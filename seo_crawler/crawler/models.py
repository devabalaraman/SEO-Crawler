from django.db import models

# Create your models here.

class Domain(models.Model):
    domain_name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.domain_name


class Page(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="pages")
    url = models.URLField()
    status_code = models.IntegerField()
    crawled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.url


class Insight(models.Model):
    page = models.OneToOneField(Page, on_delete=models.CASCADE, primary_key=True, related_name="insight")
    title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)
    h1 = models.JSONField(default=list)
    h2 = models.JSONField(default=list)
    h3 = models.JSONField(default=list)
    p_count = models.IntegerField(default=0)
    image_count = models.IntegerField(default=0)
    internal_links = models.IntegerField(default=0)
    external_links = models.IntegerField(default=0)
    keywords = models.JSONField(default=list)

    def __str__(self):
        return f"Insights for {self.page.url}"
