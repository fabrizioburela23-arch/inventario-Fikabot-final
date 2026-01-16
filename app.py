import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="FikaGroup Factory", layout="wide", page_icon="🏭")
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        background-color: #1e293b !important; color: #ffffff !important; 
    }
    div[data-testid="stMetricValue"] { color: #34d399; }
    .big-font { font-size:20px !important; font-weight: bold; color: #38bdf8; }
</style>
""", unsafe_allow_html=True)

# --- CONEXIÓN ---
conn = st.connection("gsheets", type=GSheetsConnection)

def cargar_datos():
    try:
        df = conn.read(worksheet="Hoja 1", ttl=0)
        df = df.dropna(how="all")
        # Asegurar tipos de datos numéricos
        df['Cantidad'] = pd.to_numeric(df['Cantidad'], errors='coerce').fillna(0)
        df['Total'] = pd.to_numeric(df['Total'], errors='coerce').fillna(0)
        return df
    except:
        return pd.DataFrame(columns=["Fecha", "Categoría", "Descripción", "Lote", "Cantidad", "Unidad", "Movimiento", "Costo Unitario", "Total", "Observaciones"])

def guardar_datos(df_nuevo):
    try:
        conn.update(worksheet="Hoja 1", data=df_nuevo)
        st.cache_data.clear() # Limpiar memoria para forzar recarga
        return True
    except Exception as e:
        st.error(f"Error al guardar en Google: {e}")
        return False

# Cargar al inicio
df = cargar_datos()

st.title("🏭 FikaGroup: Control de Producción")

# --- MENÚ PRINCIPAL ---
tab_mov, tab_prod, tab_ver = st.tabs(["📝 Compra / Venta Simple", "⚙️ Transformación (Fábrica)", "📊 Ver Inventario"])

# ==========================================
# TAB 1: MOVIMIENTOS SIMPLES (COMPRA/VENTA)
# ==========================================
with tab_mov:
    st.write("Usa esto para compras de materia prima o ventas finales.")
    c1, c2, c3 = st.columns(3)
    cat = c1.selectbox("Categoría", ["Materia Prima", "Suministros", "Producto Terminado"])
    mov = c2.selectbox("Acción", ["Compra (Entrada)", "Venta (Salida)", "Ajuste Inventario", "Muestras"])
    fecha = c3.date_input("Fecha", datetime.now())
    
    c4, c5, c6 = st.columns(3)
    desc = c4.text_input("Producto", placeholder="Ej: Tomate Redondo")
    cant = c5.number_input("Cantidad", min_value=0.01, format="%.2f")
    uni = c6.selectbox("Unidad", ["kg", "g", "unidades", "cajas", "litros"])
    
    c7, c8 = st.columns(2)
    costo = c7.number_input("Costo/Precio Unitario (Bs)", min_value=0.0, format="%.2f")
    obs = c8.text_input("Notas")

    if st.button("💾 Registrar Movimiento Simple", type="primary"):
        if desc and cant > 0:
            # Definir signo visual para reportes (aunque guardamos positivo y el tipo define)
            tipo_mov = mov
            if "Venta" in mov or "Salida" in mov or "Muestras" in mov:
                signo_cant = -cant # Para que reste en el stock visual
            else:
                signo_cant = cant
            
            nuevo = {
                "Fecha": fecha.strftime("%Y-%m-%d"),
                "Categoría": cat,
                "Descripción": desc,
                "Lote": "GEN",
                "Cantidad": signo_cant, # Guardamos con signo para facilitar sumas
                "Unidad": uni,
                "Movimiento": tipo_mov,
                "Costo Unitario": costo,
                "Total": cant * costo,
                "Observaciones": obs
            }
            df_upd = pd.concat([df, pd.DataFrame([nuevo])], ignore_index=True)
            if guardar_datos(df_upd):
                st.success("✅ Guardado correctamente")
                st.rerun()

# ==========================================
# TAB 2: TRANSFORMACIÓN (LA MAGIA)
# ==========================================
with tab_prod:
    st.markdown('<p class="big-font">Convertir Materia Prima -> Producto</p>', unsafe_allow_html=True)
    st.info("Ejemplo: Entran 10kg de Tomate (Materia Prima) -> Salen 2kg de Tomate Deshidratado (En Proceso)")
    
    col_a, col_b = st.columns(2)
    
    # LADO A: LO QUE SE GASTA (INPUT)
    with col_a:
        st.error("🔻 LO QUE SALE (Ingrediente)")
        origen_desc = st.text_input("Ingrediente a usar", placeholder="Ej: Tomate")
        origen_cant = st.number_input("Cantidad a usar", min_value=0.0, format="%.2f", key="orig_cant")
        origen_cat = st.selectbox("Categoría Origen", ["Materia Prima", "Producto en Proceso"], key="orig_cat")
    
    # LADO B: LO QUE SE CREA (OUTPUT)
    with col_b:
        st.success("NV LO QUE ENTRA (Resultado)")
        dest_desc = st.text_input("Producto Resultante", placeholder="Ej: Tomate Deshidratado")
        dest_cant = st.number_input("Cantidad Obtenida", min_value=0.0, format="%.2f", key="dest_cant")
        dest_cat = st.selectbox("Categoría Destino", ["Producto en Proceso", "Producto Terminado"], key="dest_cat")
        dest_costo = st.number_input("Costo del Resultado (Total)", help="Cuánto vale lo que acabas de producir", key="dest_cost")

    if st.button("⚙️ PROCESAR PRODUCCIÓN (Generar 2 Registros)", type="primary"):
        if origen_desc and dest_desc and origen_cant > 0:
            hoy = datetime.now().strftime("%Y-%m-%d")
            
            # 1. Registro de Salida (Resta)
            fila_salida = {
                "Fecha": hoy,
                "Categoría": origen_cat,
                "Descripción": origen_desc,
                "Lote": "PROD-OUT",
                "Cantidad": -origen_cant, # Negativo porque se gasta
                "Unidad": "kg",
                "Movimiento": "Consumo Producción",
                "Costo Unitario": 0,
                "Total": 0,
                "Observaciones": f"Usado para crear {dest_desc}"
            }
            
            # 2. Registro de Entrada (Suma)
            fila_entrada = {
                "Fecha": hoy,
                "Categoría": dest_cat,
                "Descripción": dest_desc,
                "Lote": "PROD-IN",
                "Cantidad": dest_cant, # Positivo porque se crea
                "Unidad": "kg", # Asumimos kg, podrías poner selector
                "Movimiento": "Producción Interna",
                "Costo Unitario": dest_costo / dest_cant if dest_cant > 0 else 0,
                "Total": dest_costo,
                "Observaciones": f"Producido desde {origen_desc}"
            }
            
            # Guardar ambos
            df_upd = pd.concat([df, pd.DataFrame([fila_salida]), pd.DataFrame([fila_entrada])], ignore_index=True)
            
            if guardar_datos(df_upd):
                st.balloons()
                st.success(f"✅ Éxito: Se restaron {origen_cant} de {origen_desc} y se sumaron {dest_cant} de {dest_desc}.")
                st.rerun()
        else:
            st.warning("⚠️ Faltan datos del ingrediente o del resultado.")

# ==========================================
# TAB 3: VISUALIZACIÓN
# ==========================================
with tab_ver:
    if not df.empty:
        # Agrupar por producto para ver stock real
        st.subheader("📦 Stock Actual (Inventario)")
        stock = df.groupby(["Categoría", "Descripción"])["Cantidad"].sum().reset_index()
        st.dataframe(stock, use_container_width=True)
        
        st.subheader("📝 Historial Detallado")
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
        
        # Botón de descarga excel real
        pass 
    else:
        st.info("La base de datos está vacía o no se pudo cargar.")
