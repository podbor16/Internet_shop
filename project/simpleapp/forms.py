from django import forms
from django.core.exceptions import ValidationError

from .models import Product


class ProductForm(forms.ModelForm):
    description = forms.CharField(min_length=20)

    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'category',
            'price',
            'quantity',
        ]

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name[0].islower():
            raise ValidationError('Название должно начинаться с заглавной буквы')
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        description = cleaned_data.get('description')

        if name == description:
            raise ValidationError({
                'name': 'Название и описание не должны совпадать'
            })

        return cleaned_data
