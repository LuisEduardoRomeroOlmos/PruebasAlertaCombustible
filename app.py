import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

# --- Configuración de la página ---
st.set_page_config(layout="wide", page_title="Dashboard Control de Combustible")

# --- Carga de datos ---
@st.cache_data
def load_data():
    try:
        df_trips = pd.read_csv('trips_data.csv')
        df_vehicles = pd.read_csv('vehicles_data.csv')
        df_routes = pd.read_csv('routes_data.csv')
        df_fuel_prices = pd.read_csv('fuel_prices_data.csv')
    except FileNotFoundError as e:
        st.error(f"Error cargando archivos: {e}")
        return pd.DataFrame(), pd.DataFrame()

    # Renombrar columnas para sincronizar con trips
    df_vehicles.rename(columns={'age_years': 'vehicle_age_years'}, inplace=True)
    df_routes.rename(columns={'distance_km': 'route_distance_km'}, inplace=True)

    # Convertir fechas
    for df, col in [
        (df_trips, 'date'),
        (df_fuel_prices, 'date'),
        (df_vehicles, 'last_maintenance')
    ]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')

    # Fusionar dataframes
    df_trips = pd.merge(df_trips, df_vehicles, on='vehicle_id', how='left', suffixes=('', '_veh'))
    df_trips = pd.merge(df_trips, df_routes, on='route_id', how='left', suffixes=('', '_route'))

    # Completar columnas principales
    if 'vehicle_type_veh' in df_trips.columns:
        df_trips['vehicle_type'] = df_trips['vehicle_type'].fillna(df_trips['vehicle_type_veh'])
    if 'terrain_route' in df_trips.columns:
        df_trips['terrain'] = df_trips['terrain'].fillna(df_trips['terrain_route'])
    if 'route_distance_km_route' in df_trips.columns:
        df_trips['route_distance_km'] = df_trips['route_distance_km'].fillna(df_trips['route_distance_km_route'])

    # Eliminar columnas redundantes
    cols_to_drop = [c for c in df_trips.columns if c.endswith('_veh') or c.endswith('_route')]
    df_trips.drop(columns=cols_to_drop, inplace=True, errors='ignore')

    return df_trips, df_fuel_prices

# --- Cargar datos ---
df_trips, df_fuel_prices = load_data()

# --- Título principal ---
st.title("🚛 DASHBOARD CONTROL DE COMBUSTIBLE")
st.subheader("Análisis del Consumo de Combustible en el Transporte Terrestre de México")

# --- Barra lateral de navegación ---
st.sidebar.title("🔍 Navegación")
tab_titles = [
    "Inicio",
    "Visión General",
    "Desempeño Operativo",
    "Eficiencia Financiera",
    "Condición Técnica",
    "Control y Mejora"
]

# Inicializar variable de sesión
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Inicio"

# Radio button que actualiza la pestaña activa
selected_tab = st.sidebar.radio(
    "Selecciona una sección:", 
    tab_titles, 
    index=tab_titles.index(st.session_state.active_tab)
)
st.session_state.active_tab = selected_tab

# --- Logo en la barra lateral ---
st.sidebar.markdown("---")
try:
    logo1 = Image.open("1.png")
    st.sidebar.image(logo1, width=200)
except:
    st.sidebar.write("Logo no disponible")

# --- CONTENIDO DE CADA SECCIÓN ---

# 📌 1. INICIO
if st.session_state.active_tab == "Inicio":
    st.header("Bienvenido al Dashboard de Control de Combustible")
    st.write("Selecciona una sección desde la barra lateral:")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Ir a Visión General"):
            st.session_state.active_tab = "Visión General"
            st.rerun()
        if st.button("Ir a Desempeño Operativo"):
            st.session_state.active_tab = "Desempeño Operativo"
            st.rerun()
    with col2:
        if st.button("Ir a Eficiencia Financiera"):
            st.session_state.active_tab = "Eficiencia Financiera"
            st.rerun()
        if st.button("Ir a Condición Técnica"):
            st.session_state.active_tab = "Condición Técnica"
            st.rerun()
    with col3:
        if st.button("Ir a Control y Mejora"):
            st.session_state.active_tab = "Control y Mejora"
            st.rerun()

# 📊 2. VISIÓN GENERAL
elif st.session_state.active_tab == "Visión General":
    st.header("Visión General")
    st.write("Panorama ejecutivo del gasto de combustible.")

    total_fuel_cost = df_trips['fuel_cost_mxn'].sum()
    total_distance = df_trips['actual_distance_km'].sum()
    avg_kpl = df_trips['kpl'].mean()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Costo Total de Combustible", f"${total_fuel_cost:,.2f} MXN")
    with col2:
        st.metric("Distancia Total Recorrida", f"{total_distance:,.2f} km")
    with col3:
        st.metric("Rendimiento Promedio", f"{avg_kpl:,.2f} km/L")

    # Tendencia mensual de costo
    if 'date' in df_trips.columns:
        st.subheader("Tendencia de Costo de Combustible por Mes")
        monthly_cost = df_trips.set_index('date')['fuel_cost_mxn'].resample('M').sum()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(monthly_cost.index, monthly_cost.values, marker='o', color="#0072B2", label="Costo Combustible")
        ax.set_title('Costo Mensual de Combustible')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Costo (MXN)')
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

    # Tendencia de precio promedio semanal
    if not df_fuel_prices.empty and 'price_per_liter_mxn' in df_fuel_prices.columns:
        st.subheader("Tendencia del Precio Promedio del Combustible")
        df_fuel_prices = df_fuel_prices.set_index('date').sort_index()
        weekly_price = df_fuel_prices['price_per_liter_mxn'].resample('W').mean()
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(weekly_price.index, weekly_price.values, marker='o', color="#D55E00", label="Precio promedio semanal")
        ax.set_title("Precio Promedio Semanal del Combustible")
        ax.set_xlabel("Fecha")
        ax.set_ylabel("Precio (MXN/L)")
        ax.grid(True)
        ax.legend()
        st.pyplot(fig)

# ⚙️ 3. DESEMPEÑO OPERATIVO
elif st.session_state.active_tab == "Desempeño Operativo":
    st.header("Desempeño Operativo")
    st.write("Análisis de cómo la operación influye en el consumo de combustible.")

    if 'vehicle_type' in df_trips.columns and 'kpl' in df_trips.columns:
        st.subheader("Rendimiento Promedio por Tipo de Vehículo")
        avg_kpl_by_vehicle_type = df_trips.groupby('vehicle_type')['kpl'].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=avg_kpl_by_vehicle_type.index, y=avg_kpl_by_vehicle_type.values, ax=ax, palette="Blues_r")
        ax.set_title('Rendimiento Promedio (km/L) por Tipo de Vehículo')
        ax.set_xlabel('Tipo de Vehículo')
        ax.set_ylabel('km/L')
        plt.xticks(rotation=15)
        st.pyplot(fig)

    if 'terrain' in df_trips.columns and 'kpl' in df_trips.columns:
        st.subheader("Rendimiento Promedio por Tipo de Terreno")
        avg_kpl_by_terrain = df_trips.groupby('terrain')['kpl'].mean().sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=avg_kpl_by_terrain.index, y=avg_kpl_by_terrain.values, ax=ax, palette="Greens_r")
        ax.set_title('Rendimiento Promedio (km/L) por Terreno')
        ax.set_xlabel('Terreno')
        ax.set_ylabel('km/L')
        plt.xticks(rotation=15)
        st.pyplot(fig)

# 💰 4. EFICIENCIA FINANCIERA
elif st.session_state.active_tab == "Eficiencia Financiera":
    st.header("Eficiencia Financiera")
    st.write("Impacto del combustible en los costos y la rentabilidad.")
    st.info("Contenido en desarrollo...")

# 🔧 5. CONDICIÓN TÉCNICA
elif selected_tab == "Condición Técnica":
    st.header("Condición Técnica")
    st.write("Factores mecánicos o técnicos que afectan el consumo de combustible.")
    st.info("Contenido en desarrollo...")

# 📈 6. CONTROL Y MEJORA
elif selected_tab == "Control y Mejora":
    st.header("Control y Mejora")
    st.write("Monitoreo y calidad de datos para optimizar el consumo.")
    st.info("Contenido en desarrollo...")
