from django.contrib.auth.backends import ModelBackend, UserModel
from accounts.models import UserProxy
from django.db.models import Q

class ProxiedModelBackend(ModelBackend):
    def get_user(self, user_id):
        try:
            return UserProxy.objects.get(pk=user_id)
        except Nuser.DoesNotExist:
            return None

class EmailOrUsernameBackend(ProxiedModelBackend):
    def authenticate(self, request, username=None, password=None):
        if username is None or password is None:
            return
        try:
            user = UserModel.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
