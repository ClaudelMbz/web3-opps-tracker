import requests

# Données à envoyer à N8N via le webhook
data = {
    "opportunities": [
        {
            "title": "Test Empty ROI",
            "source": "Test_Galxe",
            "reward": "500 USD",
            "roi": "",
            "time": 5,
            "status": "New",
            "priority": "🔥 High",
            "url": "test-galxe.com/airdrop2",
            "date": "5 août 2025",
            "hash": "test_hash_002"
        },
        {
            "title": "Test High ROI Airdrop",
            "source": "Test_Galxe",
            "reward": "500 USD",
            "roi": 100,
            "time": 5,
            "status": "New",
            "priority": "🔥 High",
            "url": "test-galxe.com/airdrop1",
            "date": "5 août 2025",
            "hash": "test_hash_001"
        },
        {
            "title": "Test Notion Integration",
            "source": "Galxe",
            "reward": "100 USD",
            "roi": 20,
            "time": 5,
            "status": "New",
            "priority": "🔥 High",
            "url": "galxe.com/test",
            "date": "5 août 2025",
            "hash": "notion_test_001"
        }
    ],
    "webhookUrl": "https://n8n-cmh9.onrender.com/webhook-test/webhook",
    "executionMode": "test"
}

# URL de ton webhook N8N (extrait du champ webhookUrl pour éviter doublon)
webhook_url = data["webhookUrl"]

# Envoi des données au webhook
response = requests.post(webhook_url, json=data)

# Affichage du résultat
print(f"Statut HTTP : {response.status_code}")
print("Réponse du serveur :", response.text)
