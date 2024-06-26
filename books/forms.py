from django import forms


class EbookForm(forms.Form):
    CHOICES = (
        ("Polish", "Polski"),
        ("Ukrainian", "Ukraiński"),
        ("English", "Angielski")
    )
    NUMBER_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5)
    )
    title = forms.CharField(max_length=100, label='')
    language = forms.ChoiceField(
        choices=CHOICES, label='W jakim języku ma powstać książka?')
    chapters = forms.ChoiceField(
        choices=NUMBER_CHOICES, label='Ile ma mieć rozdziałów?')
    subchapters = forms.ChoiceField(
        choices=NUMBER_CHOICES, label='Ile podrozdziałów?')
