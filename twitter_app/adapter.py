from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import get_user_model

User = get_user_model()

class CustomAccountAdapter(DefaultAccountAdapter):
    def generate_unique_username(self, txts, regex=None):
        for i in range(1, 1000):
            candidates = f"@githubuser{i}"
            if not User.objects.filter(username=candidates).exists():
                return candidates
        raise Exception("Could not find a unique @githubuser username")