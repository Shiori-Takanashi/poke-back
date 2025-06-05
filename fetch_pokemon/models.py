from django.db import models

class PokemonSpecies(models.Model):
    index = models.CharField(max_length=10, unique=True)  # indexはゼロパディングする
    url = models.CharField(max_length=100)
    json_data = models.JSONField(blank=True, null=True)  # JSON形式のデータを格納

    class Meta:
        verbose_name = "species"
        verbose_name_plural = "species"  # ← 明示的に指定

    def __str__(self):
        return f"Species {self.index}"

class Pokemon(models.Model):
    index = models.CharField(max_length=10, unique=True)  # indexはゼロパディングする
    url = models.CharField(max_length=100)
    json_data = models.JSONField(blank=True, null=True)  # JSON形式のデータを格納

    def __str__(self):
        return f"Pokemon {self.index}"

class PokemonForm(models.Model):
    index = models.CharField(max_length=10, unique=True)  # indexはゼロパディングする
    url = models.CharField(max_length=100)
    json_data = models.JSONField(blank=True, null=True)  # JSON形式のデータを格納

    class Meta:
        verbose_name = "form"
        verbose_name_plural = "forms"  # ← 明示的に指定

    def __str__(self):
        return f"Form {self.index}"
