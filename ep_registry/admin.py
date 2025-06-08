from django.contrib import admin

from .models import Endpoint


@admin.register(Endpoint)
class EndpointAdmin(admin.ModelAdmin):
    readonly_fields = ("id", "category", "name", "url")  # 変更させたくない項目
    list_display = ("id", "name", "using")
    fields = ["id", "category", "name", "url", "description", "using"]
    ordering = ["id"]
    actions = ["change_using_true", "change_using_false"]

    def has_add_permission(self, request):
        return False

    @admin.action(description="一斉にusing=Trueに変更")
    def change_using_true(self, request, queryset):
        count = queryset.update(using=True)
        self.message_user(request, f"{count}件をusing=Trueにしました。")

    @admin.action(description="一斉にusing=Falseに変更")
    def change_using_false(self, request, queryset):
        count = queryset.update(using=False)
        self.message_user(request, f"{count}件をusing=Falseにしました。")
