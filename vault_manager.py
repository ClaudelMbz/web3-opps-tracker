import os
import hvac

class VaultManager:
    def __init__(self, url="http://localhost:8200", token=None):
        if token is None:
            token = os.getenv("VAULT_TOKEN")
        if not token:
            raise ValueError("Token Vault non fourni. Définissez la variable d'environnement VAULT_TOKEN.")
        self.client = hvac.Client(url=url, token=token)
        if not self.client.is_authenticated():
            raise Exception("Erreur d'authentification avec Vault")

    def retrieve_secret(self, path):
        secret = self.client.secrets.kv.v2.read_secret_version(path=path)
        return secret['data']['data']



