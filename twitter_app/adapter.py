from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import generate_unique_username

class CustomAccountAdapter(DefaultAccountAdapter):
    def generate_unique_username(self, txts, regex=None):
        return generate_unique_username(
            ['@githubuser'],
            regex=r'^@[\w]+$',
            )