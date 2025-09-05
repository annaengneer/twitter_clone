from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import generate_unique_username

class CustomAccountAdapter(DefaultAccountAdapter):
    def generate_unique_username(self, txts, regex=None):
        candidates = [f'@githubuser{i}' for i in range(1, 1000)]
        return generate_unique_username(candidates,regex=r'^@[\w]+$')