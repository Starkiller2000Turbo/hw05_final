from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        labels = {
            'username': 'Логин пользователя',
        }
        fields = ('first_name', 'last_name', 'username', 'email')
