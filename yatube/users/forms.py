from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_username(self):
        data = self.cleaned_data["username"]
        forbidden_usernames = ["admin", "about", "follow", "new", "404", "500"]
        if data in forbidden_usernames:
            raise forms.ValidationError(
                f"Вы не можете использовать имя {data}. Выберите другое имя.")
        return data
