import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión FikaGroup", layout="wide", page_icon="🏭")

# Estilos CSS
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        background-color: #1e293b !important; color: #ffffff !important; 
    }
    /* Colores para métricas */
    div[data-testid="stMetricValue"] { color: #34d399; } 
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("🏭 Gestión de Producción y Ventas")
with col_header_2:
    st.write(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")

# --- MEMORIA TEMPORAL ---
if 'data' not in st.session_state:
    # Agregamos la columna 'Categoría' que antes no existía
    st.session_state.data = pd.DataFrame(columns=[
        "Fecha", "Categoría", "Descripción", "Lote", "Cantidad", "Unidad", 
        "Movimiento", "Costo Unitario", "Total", "Observaciones"
    ])

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.header("⚙️ Opciones")
    if st.button("🗑️ Resetear Base de Datos"):
        st.session_state.data = st.session_state.data.iloc[0:0]
        st.rerun()
    st.info("Aquí podrás filtrar tus reportes más adelante.")

# --- FORMULARIO DE INGRESO ---
st.subheader("📝 Registrar Operación")

with st.container():
    # Fila 1: Qué es y Qué pasó
    c1, c2, c3, c4 = st.columns(4)
    categoria = c1.selectbox("Categoría del Item", ["Materia Prima", "Producto en Proceso", "Producto Terminado", "Suministros"])
    movimiento = c2.selectbox("Tipo de Movimiento", ["Compra/Entrada", "Producción (+)", "Venta (-)", "Consumo Interno (-)", "Ajuste/Merma"])
    desc = c3.text_input("Descripción (Ej: Tomate, Salsa Picante)")
    lote = c4.text_input("Lote", value="GEN-" + datetime.now().strftime("%m%d"))

    # Fila 2: Cuánto y a qué precio
    c5, c6, c7, c8 = st.columns(4)
    cant = c5.number_input("Cantidad", min_value=0.0, format="%.2f")
    unidad = c6.selectbox("Unidad", ["kg", "litros", "botellas", "cajas", "g"])
    costo = c7.number_input("Precio/Costo Unitario (Bs)", min_value=0.0, format="%.2f")
    obs = c8.text_input("Observaciones")

    # Botón gigante de guardar
    if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
        if desc and cant > 0:
            # Lógica de Signos: Si es Venta o Consumo, la cantidad es negativa para el stock visual
            # Pero guardamos el valor absoluto y el tipo de movimiento define el signo en los reportes
            
            nuevo_registro = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Categoría": categoria,
                "Descripción": desc,
                "Lote": lote,
                "Cantidad": cant,
                "Unidad": unidad,
                "Movimiento": movimiento,
                "Costo Unitario": costo,
                "Total": cant * costo,
                "Observaciones": obs
            }
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([nuevo_registro])], 
                ignore_index=True
            )
            st.success(f"✅ {movimiento} de {desc} registrado correctamente.")
        else:
            st.error("⚠️ Falta descripción o cantidad.")

# --- DASHBOARD (RESUMEN INTELIGENTE) ---
st.divider()
df = st.session_state.data

if not df.empty:
    # 1. FILTROS RÁPIDOS
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen General", "🍅 Materia Prima", "🌶️ Prod. Terminado / Ventas", "📋 Tabla Completa"])
    
    with tab1:
        # Calcular Ventas Totales (Dinero que entró)
        ventas = df[df['Movimiento'] == 'Venta (-)']['Total'].sum()
        # Calcular Compras (Dinero que salió)
        compras = df[df['Movimiento'] == 'Compra/Entrada']['Total'].sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Ventas Totales", f"Bs {ventas:,.2f}")
        m2.metric("💸 Gastos en Compras", f"Bs {compras:,.2f}")
        m3.metric("📈 Balance (Ventas - Compras)", f"Bs {ventas - compras:,.2f}", delta_color="normal")

    with tab2:
        st.write("### Inventario de Materia Prima")
        # Filtramos solo lo que sea Materia Prima
        df_mp = df[df['Categoría'] == 'Materia Prima']
        st.dataframe(df_mp, use_container_width=True)

    with tab3:
        col_a, col_b = st.columns(2)
        with col_a:
            st.write("### Stock Producto Terminado")
            # Mostramos todo lo que sea Producto Terminado
            st.dataframe(df[df['Categoría'] == 'Producto Terminado'], use_container_width=True)
