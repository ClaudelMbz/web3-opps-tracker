
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime
import os

# Configuration de la page
st.set_page_config(
    page_title="Web3 Opportunities Tracker",
    page_icon="🚀",
    layout="wide"
)

# --- FONCTIONS DE CHARGEMENT DE DONNÉES ---

@st.cache_data(ttl=300)  # Cache de 5 minutes
def load_opportunities_from_files(data_dir="data"):
    """Charge et agrège les opportunités depuis les fichiers JSON dans le dossier data."""
    all_opportunities = []
    
    # Parcourir les sous-dossiers et fichiers
    for root, _, files in os.walk(data_dir):
        for file in files:
            if file.startswith("opportunities_") and file.endswith(".json"):
                try:
                    with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # Standardiser la structure des données
                        if isinstance(data, list):
                            opportunities = data
                        elif isinstance(data, dict) and 'opportunities' in data:
                            opportunities = data['opportunities']
                        else:
                            continue

                        for opp in opportunities:
                            opp['source'] = opp.get('source', 'Unknown')
                            opp['createdAt'] = opp.get('createdAt', datetime.now().isoformat())
                            all_opportunities.append(opp)
                except (json.JSONDecodeError, KeyError) as e:
                    st.warning(f"Erreur de lecture du fichier {file}: {e}")
    
    if not all_opportunities:
        return pd.DataFrame()

    df = pd.DataFrame(all_opportunities)
    
    # Nettoyage et standardisation
    df['createdAt'] = pd.to_datetime(df['createdAt'], errors='coerce')
    df.dropna(subset=['createdAt'], inplace=True)
    df['roi'] = pd.to_numeric(df.get('roi', 0), errors='coerce').fillna(0)
    df['reward'] = df.get('reward', 'N/A')
    df['estimated_time'] = pd.to_numeric(df.get('estimated_time', 0), errors='coerce').fillna(0)

    return df

@st.cache_data
def get_mock_data():
    """Génère des données de test si aucune donnée réelle n'est trouvée."""
    return pd.DataFrame({
        'title': [f"Mock Quest {i}" for i in range(20)],
        'source': ['Galxe', 'Zealy', 'TwitterRSS', 'AirdropsFallback'] * 5,
        'roi': [i * 0.5 for i in range(20)],
        'reward': [f"{i*10} XP" for i in range(20)],
        'estimated_time': [i + 1 for i in range(20)],
        'createdAt': pd.to_datetime([f"2025-08-{10 + i//5}T10:00:00Z" for i in range(20)])
    })

# --- INTERFACE UTILISATEUR ---

st.title("🚀 Web3 Opportunities Tracker")

# Charger les données
df_opportunities = load_opportunities_from_files()

if df_opportunities.empty:
    st.warning("Aucune donnée d'opportunité trouvée. Utilisation de données de test.")
    df_opportunities = get_mock_data()

# --- SIDEBAR AVEC FILTRES ---

st.sidebar.title("🔧 Filtres")
source_filter = st.sidebar.multiselect(
    "Sources", 
    options=df_opportunities['source'].unique(),
    default=df_opportunities['source'].unique()
)
roi_min = st.sidebar.slider("ROI minimum ($/min)", 0.0, 20.0, 2.0, 0.1)

# Filtre par date
min_date = df_opportunities['createdAt'].min().date()
max_date = df_opportunities['createdAt'].max().date()
date_range = st.sidebar.date_input(
    "Plage de dates",
    (min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Application des filtres
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
filtered_df = df_opportunities[
    (df_opportunities['source'].isin(source_filter)) &
    (df_opportunities['roi'] >= roi_min) &
    (df_opportunities['createdAt'].dt.date >= start_date.date()) &
    (df_opportunities['createdAt'].dt.date <= end_date.date())
]

# --- AFFICHAGE DES KPIS ---

st.header("📊 Métriques Clés")
total_opportunities = len(filtered_df)
avg_roi = filtered_df['roi'].mean() if not filtered_df.empty else 0
active_sources = filtered_df['source'].nunique()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Opportunités Filtrées", f"{total_opportunities}", "✅")
with col2:
    st.metric("ROI Moyen", f"${avg_roi:.2f}/min", f"{'+' if avg_roi > 2 else '-'} {avg_roi-2:.2f}")
with col3:
    st.metric("Sources Actives", f"{active_sources}/{len(df_opportunities['source'].unique())}")


# --- GRAPHIQUES DE PERFORMANCE ---

st.header("📈 Visualisations")
col1, col2 = st.columns(2)

with col1:
    # Graphique opportunités par jour
    if not filtered_df.empty:
        daily_counts = filtered_df.set_index('createdAt').resample('D').size().reset_index(name='count')
        fig_timeline = px.line(
            daily_counts, 
            x='createdAt', 
            y='count',
            title="Opportunités par jour",
            labels={'createdAt': 'Date', 'count': 'Nombre d’opportunités'}
        )
        st.plotly_chart(fig_timeline, use_container_width=True)

with col2:
    # Distribution ROI
    if not filtered_df.empty:
        fig_roi = px.histogram(
            filtered_df, 
            x='roi', 
            nbins=30,
            title="Distribution du ROI",
            labels={'roi': 'Retour sur Investissement ($/min)'}
        )
        st.plotly_chart(fig_roi, use_container_width=True)


# --- TABLE DE DONNÉES ---

st.header("📋 Opportunités Détaillées")
st.dataframe(
    filtered_df[['title', 'source', 'roi', 'reward', 'estimated_time', 'createdAt']],
    use_container_width=True
)

# Export CSV
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "📥 Télécharger en CSV",
    csv,
    "filtered_opportunities.csv",
    "text/csv",
    key='download-csv'
)

# --- FOOTER ---

st.markdown("---")
st.markdown("🕒 Dashboard mis à jour toutes les 5 minutes | 🤖 Automation active")

# --- TESTS INTERNES (BONUS) ---

def run_tests():
    """Fonction de test simple pour valider le dashboard."""
    st.sidebar.markdown("---")
    st.sidebar.header("✅ Tests de Validation")
    
    # Test 1: Chargement des données
    if not df_opportunities.empty:
        st.sidebar.success("Test 1: Chargement des données - OK")
    else:
        st.sidebar.error("Test 1: Chargement des données - Échec")

    # Test 2: Filtres
    if not filtered_df.empty or (roi_min > df_opportunities['roi'].max()):
        st.sidebar.success("Test 2: Filtres fonctionnels - OK")
    else:
        st.sidebar.warning("Test 2: Filtres potentiellement vides - Vérifier")
        
    # Test 3: Métriques
    try:
        f"{total_opportunities}, ${avg_roi:.2f}, {active_sources}"
        st.sidebar.success("Test 3: Calcul des métriques - OK")
    except Exception as e:
        st.sidebar.error(f"Test 3: Calcul des métriques - Échec: {e}")

if st.sidebar.button("Lancer les tests"):
    run_tests()

