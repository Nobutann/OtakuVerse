from django import forms

NOTAS = [(i, str(i)) for i in range(1, 6)]

class RatingForm(forms.Form):
    nota = forms.TypedChoiceField(choices=NOTAS, coerce=int, widget=forms.RadioSelect)
    comentario = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Escreva um comentário (opcional)..."})
    )