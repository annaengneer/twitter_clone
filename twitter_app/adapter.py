from allauth.account.adapter import DefaultAccountAdapter
from allauth.utils import generate_unique_username

class CustomAccountAdapter(DefaultAccountAdapter):
    print("generate_unique_username 呼び出し OK")
    def generate_unique_username(self, txts, regex=None):
        base_username = '@githubuser'
        return generate_unique_username(
            [base_username],
            regex=r'^@[\w]+$',
            )