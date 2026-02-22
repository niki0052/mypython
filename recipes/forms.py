from django import forms
from .models import Recipe, Comment

class RecipeForm(forms.ModelForm):
    tags = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tags separated by commas (e.g., vegan, dessert, quick)'
        }),
        required=False,
        help_text='Enter tags separated by commas'
    )

    class Meta:
        model = Recipe
        fields = ['title', 'category', 'tags', 'description', 'ingredients',
                 'instructions', 'cooking_time', 'difficulty', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipe title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'List ingredients, one per line'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Step-by-step instructions'}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add your comment here...'
            })
        }