from django.contrib import admin

from .models import Endpoint

@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "category", "name", "url")  # 変更させたくない項目
    list_display = ("id", "category", "name", "using")
    fields = ["id", "category", "name", "url", "description", "using"]
    ordering = [ 'id' ]

    def has_add_permission(self, request):
        return False
