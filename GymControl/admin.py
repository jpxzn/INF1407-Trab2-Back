from django.contrib import admin
from .models import Aluno, Exercicio, Treino, TreinoExercicio

admin.site.register(Aluno)
admin.site.register(Exercicio)
admin.site.register(Treino)
admin.site.register(TreinoExercicio)