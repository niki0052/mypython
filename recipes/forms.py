from django import forms
from .models import Recipe, Comment, Rating, RecipeStep, Cookbook, ShoppingItem


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
                 'instructions', 'cooking_time', 'difficulty', 'image', 'servings',
                 'calories', 'proteins', 'fats', 'carbohydrates']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Recipe title'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief description'}),
            'ingredients': forms.Textarea(attrs={'class': 'form-control', 'rows': 6, 'placeholder': 'List ingredients, one per line'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 8, 'placeholder': 'Step-by-step instructions'}),
            'cooking_time': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes'}),
            'difficulty': forms.Select(attrs={'class': 'form-control'}),
            'servings': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Number of servings'}),
            'calories': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Total calories'}),
            'proteins': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Proteins (g)', 'step': '0.1'}),
            'fats': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fats (g)', 'step': '0.1'}),
            'carbohydrates': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Carbohydrates (g)', 'step': '0.1'}),
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


class ReplyForm(forms.ModelForm):
    """Форма для ответов на комментарии"""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Write your reply...'
            })
        }


class RatingForm(forms.ModelForm):
    """Форма для оценки рецепта"""
    score = forms.ChoiceField(
        choices=[(i, f'{i} звёзд') for i in range(1, 6)],
        widget=forms.RadioSelect(attrs={'class': 'rating-input'}),
    )

    class Meta:
        model = Rating
        fields = ['score']


class RecipeStepForm(forms.ModelForm):
    """Форма для шага приготовления"""
    class Meta:
        model = RecipeStep
        fields = ['step_number', 'title', 'description', 'image', 'duration']
        widgets = {
            'step_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Step title (optional)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe this step...'}),
            'duration': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minutes (optional)', 'min': 0}),
        }


RecipeStepFormSet = forms.inlineformset_factory(
    Recipe, RecipeStep, form=RecipeStepForm,
    extra=3, can_delete=True
)


class CookbookForm(forms.ModelForm):
    """Форма для кулинарной книги"""
    class Meta:
        model = Cookbook
        fields = ['name', 'description', 'is_public', 'cover_image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cookbook name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe your cookbook...'}),
        }


class ShoppingItemForm(forms.ModelForm):
    """Форма для элемента списка покупок"""
    class Meta:
        model = ShoppingItem
        fields = ['name', 'quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item name'}),
            'quantity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quantity (e.g., 2 kg, 3 pieces)'}),
        }


class AddRecipeToShoppingListForm(forms.Form):
    """Форма для добавления ингредиентов рецепта в список покупок"""
    ingredients = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        recipe = kwargs.pop('recipe', None)
        super().__init__(*args, **kwargs)
        if recipe:
            # Парсим ингредиенты из рецепта
            ingredient_lines = [line.strip() for line in recipe.ingredients.split('\n') if line.strip()]
            self.fields['ingredients'].choices = [(i, line) for i, line in enumerate(ingredient_lines)]
