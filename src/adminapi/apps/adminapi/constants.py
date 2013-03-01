from .forms import UserCreationForm

ADMIN_FORM_OVERRIDES = {
    'user': UserCreationForm
}
