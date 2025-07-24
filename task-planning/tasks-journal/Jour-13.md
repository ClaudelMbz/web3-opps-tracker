# 🗓️ Jour 13 : Tests & CI/CD

## 🎯 Objectif du Jour
- Configurer GitHub Actions pour CI/CD
- Automatiser les tests sur chaque commit
- Pipeline de déploiement automatisé
- Coverage et qualité du code

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** GitHub Actions Setup
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
```
**Livrable :** Pipeline CI/CD fonctionnel

---

## ⏰ Créneau 2-5 : Optimisation et Tests
- Tests unitaires coverage > 90%
- Tests d'intégration automatisés
- Linting et formatting (black, flake8)
- Security scan avec bandit
- Badge coverage GitHub

**Livrable :** Pipeline de qualité complet
