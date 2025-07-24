# 🗓️ Jour 9 : Dashboard Streamlit

## 🎯 Objectif du Jour
- Créer un dashboard interactif avec Streamlit
- Visualiser les métriques et KPIs du projet
- Implémenter les filtres et graphiques
- Interface utilisateur intuitive

---

## ⏰ Créneau 1 : 0:00 - 0:30
**Tâche :** Setup Streamlit  
**Action :**
```bash
pip install streamlit plotly pandas
streamlit hello  # Test installation
```
```python
# dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
import json

st.set_page_config(
    page_title="Web3 Opportunities Tracker",
    page_icon="🚀",
    layout="wide"
)
```
**Livrable :** Environnement Streamlit fonctionnel

---

## ⏰ Créneau 2 : 0:30 - 1:00
**Tâche :** Layout et Sidebar  
**Action :**
```python
# Sidebar pour filtres
st.sidebar.title("🔧 Filtres")
source_filter = st.sidebar.multiselect(
    "Sources", ["Galxe", "Zealy", "TwitterRSS", "AirdropsFallback"]
)
roi_min = st.sidebar.slider("ROI minimum ($/min)", 0.0, 10.0, 2.0)
date_range = st.sidebar.date_input("Plage de dates")

# Main layout
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Opportunités", "127", "↗️ +23")
with col2:
    st.metric("ROI Moyen", "$3.2/min", "↗️ +0.4")
with col3:
    st.metric("Sources Actives", "4/4", "✅")
```
**Livrable :** Interface avec filtres et métriques principales

---

## ⏰ Créneau 3 : 1:00 - 1:30
**Tâche :** Graphiques de Performance  
**Action :**
```python
# Graphique opportunités par jour
fig_timeline = px.line(
    df_timeline, 
    x='date', 
    y='count', 
    color='source',
    title="Opportunités par jour et par source"
)
st.plotly_chart(fig_timeline, use_container_width=True)

# Distribution ROI
fig_roi = px.histogram(
    df_opportunities, 
    x='roi', 
    nbins=20,
    title="Distribution du ROI"
)
st.plotly_chart(fig_roi, use_container_width=True)
```
**Livrable :** Graphiques interactifs opérationnels

---

## ⏰ Créneau 4 : 1:30 - 2:00
**Tâche :** Table de Données  
**Action :**
```python
# Table des opportunités filtrées
st.subheader("📋 Opportunités Récentes")
filtered_df = df_opportunities[
    (df_opportunities['roi'] >= roi_min) & 
    (df_opportunities['source'].isin(source_filter))
]

st.dataframe(
    filtered_df[['title', 'source', 'roi', 'reward', 'estimated_time']],
    use_container_width=True
)

# Possibilité d'export CSV
csv = filtered_df.to_csv(index=False)
st.download_button(
    "📥 Télécharger CSV",
    csv,
    "opportunities.csv",
    "text/csv"
)
```
**Livrable :** Table interactive avec export

---

## ⏰ Créneau 5 : 2:00 - 2:30
**Tâche :** Intégration et Déploiement  
**Action :**
```python
# Connexion aux données live
@st.cache_data(ttl=300)  # Cache 5 minutes
def load_opportunities():
    # Charger depuis Google Sheets ou fichiers JSON
    with open('data/latest_opportunities.json') as f:
        return pd.DataFrame(json.load(f)['opportunities'])

# Auto-refresh
if st.button("🔄 Actualiser"):
    st.cache_data.clear()
    st.experimental_rerun()

# Footer avec stats
st.markdown("---")
st.markdown("📊 Dashboard mis à jour toutes les 5 minutes | 🤖 Automation active")
```
**Livrable :** Dashboard complet avec auto-refresh

---

## 📜 Vérification Finale
- [ ] Dashboard accessible via `streamlit run dashboard.py`
- [ ] Métriques en temps réel affichées
- [ ] Filtres fonctionnels (source, ROI, date)
- [ ] Graphiques interactifs (timeline, distribution)
- [ ] Table avec export CSV
- [ ] Auto-refresh des données

---

## 📊 Métriques Affichées
- **Total Opportunités** : Compteur global
- **ROI Moyen** : Performance moyenne
- **Sources Actives** : Statut des scrapers
- **Opportunités/Jour** : Timeline
- **Distribution ROI** : Histogram
- **Top Sources** : Graphique en secteurs

---

## 🚀 Prochaines Étapes (Jour 10)
- Workflows n8n avancés
- Healthchecks et monitoring
- Alertes automatiques

---

*Note : Lancer avec `streamlit run dashboard.py --server.port 8501`*
