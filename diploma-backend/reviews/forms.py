from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = (
            "text",
            "rating",
        )

        labels = {
            "text": "Текст отзыва",
            "rating": "Оценка",
        }

        widgets = {
            "text": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": (
                        "Введите текст отзыва"
                    ),
                },
            ),
            "rating": forms.NumberInput(
                attrs={
                    "min": 1,
                    "max": 5,
                },
            ),
        }