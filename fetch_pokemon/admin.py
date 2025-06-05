from django.contrib import admin
from .models import PokemonSpecies, Pokemon, PokemonForm

@admin.register(PokemonSpecies)
class PokemonSpeciesAdmin(admin.ModelAdmin):
    list_display = ('index', 'url')
    fields = ('index', 'url', 'json_data')


@admin.register(PokemonForm)
class PokemonFormAdmin(admin.ModelAdmin):
    list_display = ('index', 'url')
    fields = ('index', 'url', 'json_data')


@admin.register(Pokemon)
class PokemonAdmin(admin.ModelAdmin):
    list_display = ('index', 'url')
    fields = ('index', 'url', 'json_data')
