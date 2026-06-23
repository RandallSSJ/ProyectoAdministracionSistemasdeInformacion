import streamlit as st
import pandas as pd
import sqlite3
import os
import math
from datetime import datetime
from main import crear_servicio
from InfrastructureApi.usgs_adapter import USGSAdapter
from InfrastructureDataBase.sqlite_adapter import SQLiteAdapter
from Application.obtener_sismos import ObtenerSismos


st.set_page_config(
    page_title="Sistema de Monitoreo de Sismos",
    page_icon="🌋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Estilo de fuentes de Google */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Outfit', sans-serif;
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Encabezados */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        color: #f8fafc;
    }
    
    /* Contenedor del Hero Header */
    .hero-container {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.1) 0%, rgba(0, 0, 0, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    /* Tarjetas de Métricas (KPIs) */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.3);
    }
    
    /* Barra lateral */
    [data-testid="stSidebar"] {
        background-color: #0b0f19;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Botón personalizado de Streamlit */
    .stButton>button {
        background-color: #0ea5e9;
        color: #ffffff;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #38bdf8;
        transform: translateY(-1px);
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
    }
    
    /* Enlaces y Badges */
    .badge-leve {
        background-color: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    
    .badge-moderado {
        background-color: rgba(249, 115, 22, 0.15);
        color: #fb923c;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid rgba(249, 115, 22, 0.3);
    }
    
    .badge-fuerte {
        background-color: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 2px 8px;
        border-radius: 6px;
        font-weight: 600;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    
    /* Pie de página */
    .footer {
        text-align: center;
        padding: 2.5rem 0;
        font-size: 0.85rem;
        color: #64748b;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 4rem;
    }
</style>
""", unsafe_allow_html=True)

# Rutas e inicialización
DB_PATH = os.path.join(os.path.dirname(__file__), "sismos_nicaragua.db")

# Funciones de carga con cache
@st.cache_data(ttl=300)
def cargar_datos_api():
    """Obtiene datos de la API USGS filtrados para el área de Nicaragua en tiempo real."""
    try:
        
        
        url = (
            "https://earthquake.usgs.gov/fdsnws/event/1/query"
            "?format=geojson"
            "&minlatitude=10"
            "&maxlatitude=16"
            "&minlongitude=-88"
            "&maxlongitude=-82"
            "&limit=100"
        )
        import requests
        respuesta = requests.get(url, timeout=10)
        respuesta.raise_for_status()
        datos = respuesta.json()
        
        if isinstance(datos, dict) and "features" in datos:
            registros = []
            for item in datos["features"]:
                id_sismo = item.get("id")
                properties = item.get("properties", {})
                geometry = item.get("geometry", {})
                
                mag = properties.get("mag")
                lugar = properties.get("place", "Desconocido")
                
                # Conversión de timestamp (milisegundos) a string legible
                time_epoch = properties.get("time")
                fecha_str = ""
                if time_epoch:
                    try:
                        fecha_str = datetime.fromtimestamp(time_epoch / 1000).strftime("%Y-%m-%d %H:%M:%S")
                    except Exception:
                        fecha_str = str(time_epoch)
                
                coords = geometry.get("coordinates", [None, None, None])
                lon = coords[0] if len(coords) > 0 else None
                lat = coords[1] if len(coords) > 1 else None
                prof = coords[2] if len(coords) > 2 else None
                
                # Clasificación de categoría
                if mag is not None:
                    if mag < 4.0:
                        categoria = "Leve"
                    elif mag < 6.0:
                        categoria = "Moderado"
                    else:
                        categoria = "Fuerte"
                else:
                    categoria = "Desconocido"
                
                registros.append({
                    "ID": id_sismo,
                    "Fecha": fecha_str,
                    "Magnitud": mag,
                    "Profundidad (km)": prof,
                    "Lugar": lugar,
                    "Latitud": lat,
                    "Longitud": lon,
                    "Categoría": categoria,
                    "URL": properties.get("url")
                })
            return pd.DataFrame(registros)
        return pd.DataFrame()
    except Exception as e:
        st.warning(f"Error al cargar datos filtrados de Nicaragua desde la API: {e}. Intentando fallback...")
        # Fallback al adaptador estándar que obtiene datos globales y luego los filtra
        try:
            repo = USGSAdapter()
            servicio = ObtenerSismos(repo)
            datos = servicio.ejecutar()
            
            if isinstance(datos, dict) and "features" in datos:
                registros = []
                for item in datos["features"]:
                    id_sismo = item.get("id")
                    properties = item.get("properties", {})
                    geometry = item.get("geometry", {})
                    
                    mag = properties.get("mag")
                    lugar = properties.get("place", "Desconocido")
                    
                    time_epoch = properties.get("time")
                    fecha_str = ""
                    if time_epoch:
                        try:
                            fecha_str = datetime.fromtimestamp(time_epoch / 1000).strftime("%Y-%m-%d %H:%M:%S")
                        except Exception:
                            fecha_str = str(time_epoch)
                    
                    coords = geometry.get("coordinates", [None, None, None])
                    lon = coords[0] if len(coords) > 0 else None
                    lat = coords[1] if len(coords) > 1 else None
                    prof = coords[2] if len(coords) > 2 else None
                    
                    if mag is not None:
                        categoria = "Leve" if mag < 4.0 else ("Moderado" if mag < 6.0 else "Fuerte")
                    else:
                        categoria = "Desconocido"
                    
                    registros.append({
                        "ID": id_sismo,
                        "Fecha": fecha_str,
                        "Magnitud": mag,
                        "Profundidad (km)": prof,
                        "Lugar": lugar,
                        "Latitud": lat,
                        "Longitud": lon,
                        "Categoría": categoria,
                        "URL": properties.get("url")
                    })
                df = pd.DataFrame(registros)
                # Filtrar estrictamente para conservar solo Nicaragua
                if not df.empty:
                    df = df[
                        (df["Latitud"].between(10.0, 16.0)) & 
                        (df["Longitud"].between(-88.0, -82.0))
                    ]
                return df
        except Exception:
            pass
        return pd.DataFrame()

@st.cache_data(ttl=60)
def cargar_datos_db():
    """Consulta la vista completa de la base de datos SQLite local."""
    try:
        if not os.path.exists(DB_PATH):
            return pd.DataFrame()
            
        conexion = sqlite3.connect(DB_PATH)
        query = """
        SELECT
            id_sismo as ID,
            fecha as Fecha,
            magnitud as Magnitud,
            profundidad as "Profundidad (km)",
            nombre as Lugar,
            latitud as Latitud,
            longitud as Longitud,
            nombre_categoria as Categoría
        FROM vista_sismos_completa
        """
        df = pd.read_sql_query(query, conexion)
        conexion.close()
        # Agregar enlace nulo ya que la base de datos no lo almacena
        df["URL"] = None
        return df
    except Exception as e:
        st.warning(f"Error al cargar la vista de BD: {e}. Intentando fallback...")
        try:
            # Fallback al SQLiteAdapter estándar
            repo = SQLiteAdapter()
            servicio = ObtenerSismos(repo)
            datos = servicio.ejecutar()
            # datos es una lista de tuplas: (id_sismo, fecha, magnitud, profundidad)
            df = pd.DataFrame(datos, columns=["ID", "Fecha", "Magnitud", "Profundidad (km)"])
            df["Lugar"] = "Nicaragua (Fallback BD)"
            df["Categoría"] = df["Magnitud"].apply(lambda m: "Leve" if m < 4.0 else ("Moderado" if m < 6.0 else "Fuerte"))
            df["Latitud"] = None
            df["Longitud"] = None
            df["URL"] = None
            return df
        except Exception as ex:
            st.error(f"Error en fallback de base de datos: {ex}")
            return pd.DataFrame()

def renderizar_mapa_nicaragua(df):
    """Muestra un mapa interactivo y zoomable de Nicaragua con marcadores de sismos."""
    df_map = df.dropna(subset=["Latitud", "Longitud"]).copy()
    
    if df_map.empty:
        st.warning("⚠️ No hay coordenadas geográficas disponibles en el conjunto de datos para mostrar el mapa.")
        return
        
    st.markdown("### Epicentros en el Mapa de Nicaragua")
    st.write("Haga zoom e interactúe con el mapa. Pase el cursor sobre los círculos para ver detalles básicos, o haga clic para ver información extendida.")
    
    # Intentar usar streamlit-folium y folium (mapa Leaflet / OpenStreetMap interactivo)
    try:
        import folium
        from streamlit_folium import st_folium
        
        # Coordenadas por defecto (Centro de Nicaragua)
        lat_c = 12.8654
        lon_c = -85.2072
        zoom_inicial = 7
        
        # Si la mayoría de los sismos están fuera de Nicaragua (ej. API USGS global), centrar dinámicamente
        df_nicaragua = df_map[
            (df_map["Latitud"].between(10.0, 16.0)) & 
            (df_map["Longitud"].between(-89.0, -81.0))
        ]
        
        if not df_nicaragua.empty:
            lat_c = df_nicaragua["Latitud"].mean()
            lon_c = df_nicaragua["Longitud"].mean()
        else:
            lat_c = df_map["Latitud"].mean()
            lon_c = df_map["Longitud"].mean()
            zoom_inicial = 4
            
        # Crear mapa folium
        mapa = folium.Map(
            location=[lat_c, lon_c],
            zoom_start=zoom_inicial,
            control_scale=True,
            tiles="OpenStreetMap"
        )
        
        # Agregar marcadores circulares
        for _, fila in df_map.iterrows():
            lat = fila["Latitud"]
            lon = fila["Longitud"]
            mag = fila["Magnitud"]
            prof = fila["Profundidad (km)"]
            lugar = fila["Lugar"]
            fecha = fila["Fecha"]
            cat = fila["Categoría"]
            
            # Asignación de colores
            if cat == "Leve":
                color = "#22c55e" # Verde
            elif cat == "Moderado":
                color = "#fb923c" # Naranja
            else:
                color = "#ef4444" # Rojo
                
            popup_html = f"""
            <div style="font-family: 'Outfit', sans-serif; font-size: 12px; line-height: 1.4; width: 180px;">
                <h4 style="margin: 0 0 5px 0; color: {color};">Sismo {cat}</h4>
                <b>Lugar:</b> {lugar}<br/>
                <b>Magnitud:</b> {mag} Richter<br/>
                <b>Profundidad:</b> {prof} km<br/>
                <b>Fecha:</b> {fecha}
            </div>
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=float(mag) * 2.2 + 2,
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"Mag: {mag} - {lugar}",
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.6,
                weight=1.5
            ).add_to(mapa)
            
        # Renderizar folium en Streamlit
        st_folium(mapa, width="100%", height=550, returned_objects=[])
        
    except Exception:
        # Fallback a Plotly Express scatter_mapbox (mapa de carreteras formal OSM sin token)
        try:
            import plotly.express as px
            
            df_nicaragua = df_map[
                (df_map["Latitud"].between(10.0, 16.0)) & 
                (df_map["Longitud"].between(-89.0, -81.0))
            ]
            if not df_nicaragua.empty:
                lat_c = df_nicaragua["Latitud"].mean()
                lon_c = df_nicaragua["Longitud"].mean()
                zoom_lvl = 6.5
            else:
                lat_c = df_map["Latitud"].mean()
                lon_c = df_map["Longitud"].mean()
                zoom_lvl = 3.5
                
            fig = px.scatter_mapbox(
                df_map,
                lat="Latitud",
                lon="Longitud",
                color="Categoría",
                size="Magnitud",
                hover_name="Lugar",
                hover_data={
                    "Fecha": True, 
                    "Magnitud": True, 
                    "Profundidad (km)": True, 
                    "Categoría": False, 
                    "Latitud": False, 
                    "Longitud": False
                },
                color_discrete_map={"Leve": "#22c55e", "Moderado": "#fb923c", "Fuerte": "#ef4444"},
                zoom=zoom_lvl,
                center={"lat": lat_c, "lon": lon_c},
                height=550
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":0,"l":0,"b":0},
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception:
            # Fallback definitivo a st.map estándar (Mapbox básico de Streamlit)
            df_std_map = df_map.rename(columns={"Latitud": "latitude", "Longitud": "longitude"})
            st.map(df_std_map)

# ----------------- PANEL LATERAL / SIDEBAR -----------------
st.sidebar.markdown("""
<div style="text-align: center; padding: 1rem 0;">
    <h2 style="color: #38bdf8; margin: 0;">🌋 SISMOS DETECTOR</h2>
    <p style="color: #64748b; font-size: 0.85rem;">Panel de Control y Filtros</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.subheader("Origen de Información")
origen = st.sidebar.radio(
    "Seleccione una fuente:",
    ["API USGS (En tiempo real)", "Base de Datos Local (Histórico)"],
    index=0
)

# Carga de datos
if origen == "API USGS (En tiempo real)":
    df_raw = cargar_datos_api()
    if df_raw.empty:
        st.sidebar.warning("API no disponible, cargando respaldo de base de datos...")
        df_raw = cargar_datos_db()
        origen_actual = "Base de Datos (Autorespaldo)"
    else:
        origen_actual = "API USGS (Nicaragua)"
else:
    df_raw = cargar_datos_db()
    origen_actual = "Base de Datos SQLite (Nicaragua)"

# Barra lateral: Indicador de origen
st.sidebar.markdown(f"""
<div style="background-color: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 8px 12px; margin-bottom: 20px;">
    <span style="color: #38bdf8; font-weight: 600; font-size: 0.85rem;">Fuente Activa:</span><br/>
    <span style="color: #f1f5f9; font-size: 0.85rem;">{origen_actual}</span>
</div>
""", unsafe_allow_html=True)

# Barra lateral: Filtros
st.sidebar.subheader("Filtros de Búsqueda")

search_query = st.sidebar.text_input("🔍 Buscar por lugar / ubicación:", "", placeholder="Ej: Nicaragua, Alaska...").strip()

# Valores por defecto para sliders
min_mag = 0.0
max_mag = 10.0
max_depth = 500.0

if not df_raw.empty:
    actual_min_mag = float(df_raw["Magnitud"].min()) if not pd.isna(df_raw["Magnitud"].min()) else 0.0
    actual_max_mag = float(df_raw["Magnitud"].max()) if not pd.isna(df_raw["Magnitud"].max()) else 10.0
    actual_max_depth = float(df_raw["Profundidad (km)"].max()) if not pd.isna(df_raw["Profundidad (km)"].max()) else 300.0
    
    # Ajustar rangos válidos
    min_mag = max(0.0, min(actual_min_mag, 10.0))
    max_mag = min(10.0, max(actual_max_mag, 0.0))
    if min_mag >= max_mag:
        min_mag = 0.0
        max_mag = 10.0
        
    max_depth = max(10.0, actual_max_depth)

mag_range = st.sidebar.slider(
    "Escala de Magnitud (Richter):",
    min_value=0.0,
    max_value=10.0,
    value=(float(min_mag), float(max_mag)),
    step=0.1
)

depth_limit = st.sidebar.slider(
    "Profundidad Máxima (km):",
    min_value=0.0,
    max_value=float(math.ceil(max_depth / 50.0) * 50.0),
    value=float(math.ceil(max_depth / 50.0) * 50.0),
    step=5.0
)

# Botón reset
if st.sidebar.button("🔄 Restablecer Filtros"):
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()

# Filtrado de datos
df_filtered = df_raw.copy()

if not df_filtered.empty:
    if search_query:
        df_filtered = df_filtered[df_filtered["Lugar"].str.contains(search_query, case=False, na=False)]
    
    df_filtered = df_filtered[
        (df_filtered["Magnitud"] >= mag_range[0]) &
        (df_filtered["Magnitud"] <= mag_range[1]) &
        (df_filtered["Profundidad (km)"] <= depth_limit)
    ]
    
    # Restringir estrictamente al mapa/región de Nicaragua
    if "Latitud" in df_filtered.columns and "Longitud" in df_filtered.columns:
        df_filtered = df_filtered[
            (df_filtered["Latitud"].between(10.0, 16.0) | df_filtered["Latitud"].isna()) &
            (df_filtered["Longitud"].between(-88.0, -82.0) | df_filtered["Longitud"].isna())
        ]

# ----------------- PANEL PRINCIPAL -----------------
# Hero Header
st.markdown("""
<div class="hero-container">
    <h1 style="margin: 0; color: #f8fafc; font-size: 2.5rem; font-weight: 700;">🌋 Monitoreo y Análisis de Sismos</h1>
    <p style="margin: 0.5rem 0 0 0; color: #94a3b8; font-size: 1.1rem; font-weight: 300;">
        Plataforma interactiva para la exploración de sismos en tiempo real e históricos de Nicaragua.
    </p>
</div>
""", unsafe_allow_html=True)

# Validar si hay datos
if df_raw.empty:
    st.error("❌ No se pudieron cargar datos desde el origen seleccionado. Por favor, intente con la otra fuente en el panel izquierdo.")
else:
    # Cálculo de métricas
    if not df_filtered.empty:
        total_sismos = len(df_filtered)
        max_mag_val = df_filtered["Magnitud"].max()
        avg_depth_val = df_filtered["Profundidad (km)"].mean()
        
        fuerte_count = len(df_filtered[df_filtered["Categoría"] == "Fuerte"])
        mod_count = len(df_filtered[df_filtered["Categoría"] == "Moderado"])
        
        if fuerte_count > 0:
            alerta = "🔴 FUERTE"
            alerta_color = "#f87171"
        elif mod_count > 0:
            alerta = "🟠 MODERADO"
            alerta_color = "#fb923c"
        else:
            alerta = "🟢 LEVE"
            alerta_color = "#4ade80"
    else:
        total_sismos = 0
        max_mag_val = 0.0
        avg_depth_val = 0.0
        alerta = "N/A"
        alerta_color = "#64748b"

    # Mostrar KPIs en pantalla
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Sismos Registrados</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #38bdf8; margin-top: 0.2rem;">{total_sismos}</div>
            <div style="font-size: 0.75rem; color: #64748b;">En el rango filtrado</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Magnitud Máxima</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #f43f5e; margin-top: 0.2rem;">{max_mag_val:.1f} M</div>
            <div style="font-size: 0.75rem; color: #64748b;">Escala de Richter</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Profundidad Promedio</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: #fb923c; margin-top: 0.2rem;">{avg_depth_val:.1f} km</div>
            <div style="font-size: 0.75rem; color: #64748b;">Distancia promedio al foco</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.85rem; color: #94a3b8; font-weight: 600; text-transform: uppercase;">Severidad Mayor</div>
            <div style="font-size: 2.2rem; font-weight: 700; color: {alerta_color}; margin-top: 0.2rem;">{alerta}</div>
            <div style="font-size: 0.75rem; color: #64748b;">Sismo de mayor energía</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Crear pestañas (Tabs)
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Tabla Sísmica",
        "🗺️ Mapa Sísmico",
        "📈 Gráficos Estadísticos",
        "ℹ️ Acerca del Sistema"
    ])

    # ----------------- TAB 1: TABLA ORDENADA -----------------
    with tab1:
        if df_filtered.empty:
            st.info("ℹ️ No hay registros que coincidan con los filtros aplicados en el panel lateral.")
        else:
            st.markdown("### Listado Ordenado de Eventos Sísmicos")
            st.write("Ordene los datos haciendo clic en el encabezado de las columnas de la tabla o usando el panel de abajo:")

            # Opciones de ordenación dinámicas
            col_o1, col_o2 = st.columns([3, 1])
            with col_o1:
                sort_col = st.selectbox(
                    "Ordenar la tabla prioritariamente por:",
                    ["Fecha", "Magnitud", "Profundidad (km)", "Lugar"],
                    index=0,
                    key="select_sort_col"
                )
            with col_o2:
                sort_dir = st.radio(
                    "Dirección del orden:",
                    ["Descendente", "Ascendente"],
                    horizontal=True,
                    key="radio_sort_dir"
                )

            # Ordenación del DataFrame
            asc = (sort_dir == "Ascendente")
            df_sorted = df_filtered.sort_values(by=sort_col, ascending=asc)

            # Configuración estética de las columnas en st.dataframe
            config_columnas = {
                "ID": st.column_config.TextColumn("ID Sismo", width="small", help="Código de registro único"),
                "Fecha": st.column_config.TextColumn("Fecha y Hora", width="medium"),
                "Magnitud": st.column_config.NumberColumn(
                    "Magnitud (M)",
                    format="%.1f",
                    help="Magnitud en la escala Richter"
                ),
                "Profundidad (km)": st.column_config.NumberColumn(
                    "Profundidad",
                    format="%.1f km",
                    help="Profundidad hipocentral"
                ),
                "Lugar": st.column_config.TextColumn("Ubicación", width="large"),
                "Categoría": st.column_config.TextColumn("Categoría", width="small"),
            }

            if "Latitud" in df_sorted.columns:
                config_columnas["Latitud"] = st.column_config.NumberColumn("Latitud", format="%.4f")
            if "Longitud" in df_sorted.columns:
                config_columnas["Longitud"] = st.column_config.NumberColumn("Longitud", format="%.4f")
            if "URL" in df_sorted.columns and df_sorted["URL"].notna().any():
                config_columnas["URL"] = st.column_config.LinkColumn("Enlace USGS", help="Detalles del sismo en USGS")

            # Renderizar tabla interactiva
            st.dataframe(
                df_sorted,
                use_container_width=True,
                column_config=config_columnas,
                hide_index=True
            )

            # Exportar datos
            csv_data = df_sorted.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Exportar Tabla Actual como CSV",
                data=csv_data,
                file_name=f"sismos_filtrados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

    # ----------------- TAB 2: MAPA SÍSMICO -----------------
    with tab2:
        renderizar_mapa_nicaragua(df_filtered)

    # ----------------- TAB 3: GRÁFICOS ESTADÍSTICOS -----------------
    with tab3:
        if df_filtered.empty:
            st.info("ℹ️ No hay suficientes datos para generar gráficos.")
        else:
            st.markdown("### Análisis Gráfico e Histogramas")
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Frecuencia por Categoría de Severidad")
                # Contar frecuencias de sismos
                counts = df_filtered["Categoría"].value_counts()
                orden_cat = ["Leve", "Moderado", "Fuerte"]
                counts_sorted = counts.reindex(orden_cat).fillna(0).astype(int)
                st.bar_chart(counts_sorted, color="#0ea5e9")
                
            with col_chart2:
                st.subheader("Relación Magnitud vs Profundidad")
                # Gráfico de dispersión
                st.scatter_chart(
                    df_filtered,
                    x="Profundidad (km)",
                    y="Magnitud",
                    color="Categoría",
                    size="Magnitud"
                )
                
            st.subheader("Evolución Cronológica de Magnitudes")
            df_temporal = df_filtered.sort_values(by="Fecha")
            # Gráfico de línea temporal
            st.line_chart(
                df_temporal.set_index("Fecha")["Magnitud"],
                color="#f43f5e"
            )

    # ----------------- TAB 4: ACERCA DE -----------------
    with tab4:
        st.markdown("""
        ### Sistema de Información y Monitoreo Sísmico (SISMOS)
        
        Esta aplicación proporciona herramientas de visualización y consulta sobre movimientos sísmicos detectados.
        
        #### Fuentes de Datos
        
        *   **API USGS (United States Geological Survey):** Servicio en tiempo real provisto por el gobierno de EE.UU. que recopila información sísmica a nivel mundial. La pestaña de la API carga los últimos 20 sismos globales detectados.
        *   **Base de Datos Local (Nicaragua DB):** Repositorio local estructurado mediante **SQLite3** con registros sísmicos enfocados en el área geográfica de Nicaragua. Este origen utiliza vistas optimizadas (`vista_sismos_completa`) que relacionan sismos con categorías de magnitud y lugares de forma relacional.
        
        #### Clasificación Utilizada
        
        El sistema categoriza automáticamente los sismos según los rangos estándar de magnitud:
        
        1.  🟢 **Leve:** Magnitud menor de 4.0 Richter. Generalmente no produce daños.
        2.  🟠 **Moderado:** Magnitud entre 4.0 y 5.9 Richter. Puede producir daños en construcciones débiles.
        3.  🔴 **Fuerte:** Magnitud mayor o igual a 6.0 Richter. Alta probabilidad de daños generalizados.
        
        #### Tecnologías e Integración
        
        *   **Streamlit:** Framework para interfaces web rápidas en Python.
        *   **Pydeck:** Visualización interactiva de mapas 3D/2D basada en Deck.gl.
        *   **Pandas:** Manipulación y estructuración de tablas de datos.
        *   **SQLite3:** Motor de base de datos relacional ligero.
        """)

# Footer
st.markdown("""
<div class="footer">
    <p>Sistema de Monitoreo de Sismos &copy; 2026. Todos los derechos reservados.</p>
    <p style="font-size: 0.75rem; color: #475569; margin-top: 0.2rem;">Arquitectura Limpia &bull; Diseñado para Visualizaciones Científicas</p>
</div>
""", unsafe_allow_html=True)
