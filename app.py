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
    st.info("Sistema actualizado con control de Muestras.")

# --- FORMULARIO DE INGRESO ---
st.subheader("📝 Registrar Operación")

with st.container():
    # Fila 1: Qué es y Qué pasó
    c1, c2, c3, c4 = st.columns(4)
    categoria = c1.selectbox("Categoría del Item", ["Materia Prima", "Producto en Proceso", "Producto Terminado", "Suministros"])
    
    # AQUI ESTA TU CAMBIO DE MUESTRAS
    movimiento = c2.selectbox("Tipo de Movimiento", [
        "Compra/Entrada", 
        "Producción (+)", 
        "Venta (-)", 
        "Entrega de Muestras (-)", 
        "Consumo Interno (-)", 
        "Ajuste/Merma"
    ])
    
    desc = c3.text_input("Descripción (Ej: Salsa Ya!Jua)")
    lote = c4.text_input("Lote", value="GEN-" + datetime.now().strftime("%m%d"))

    # Fila 2: Cuánto y a qué precio
    c5, c6, c7, c8 = st.columns(4)
    cant = c5.number_input("Cantidad", min_value=0.0, format="%.2f")
    
    # AQUI ESTA TU CAMBIO DE UNIDADES
    unidad = c6.selectbox("Unidad", ["kg", "unidades", "cajas"])
    
    costo = c7.number_input("Precio/Costo Unitario (Bs)", min_value=0.0, format="%.2f")
    obs = c8.text_input("Observaciones")

    # Botón de guardar
    if st.button("💾 Guardar Registro", type="primary", use_container_width=True):
        if desc and cant > 0:
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Resumen Financiero", "🍅 Materia Prima", "🌶️ Prod. Terminado / Salidas", "📋 Tabla Completa"])
    
    with tab1:
        # Calcular Ventas Totales (Dinero que entró real)
        ventas = df[df['Movimiento'] == 'Venta (-)']['Total'].sum()
        # Calcular Gastos en Compras
        compras = df[df['Movimiento'] == 'Compra/Entrada']['Total'].sum()
        # Calcular Inversión en Muestras (Dinero que regalaste en producto)
        costo_muestras = df[df['Movimiento'] == 'Entrega de Muestras (-)']['Total'].sum()
        
        col_metrics = st.columns(4)
        col_metrics[0].metric("💰 Ventas Reales", f"Bs {ventas:,.2f}")
        col_metrics[1].metric("💸 Compras MP", f"Bs {compras:,.2f}")
        col_metrics[2].metric("🎁 Inversión Muestras", f"Bs {costo_muestras:,.2f}")
        col_metrics[3].metric("📈 Flujo de Caja", f"Bs {ventas - compras:,.2f}", 
             delta="Ganancia" if (ventas-compras) > 0 else "Déficit")

    with tab2:
        st.write("### Inventario de Materia Prima")
        df_mp = df[df['Categoría'] == 'Materia Prima']
        st.dataframe(df_mp, use_container_width=True)

    with tab3:
        c_a, c_b = st.columns(2)
        with c_a:
            st.write("### Stock Producto Terminado")
            st.dataframe(df[df['Categoría'] == 'Producto Terminado'], use_container_width=True)
        with c_b:
            st.write("### Salidas (Ventas y Muestras)")
            # Mostramos Ventas y Muestras juntas para ver salida de producto
            filtro_salidas = df['Movimiento'].isin(['Venta (-)', 'Entrega de Muestras (-)'])
            st.dataframe(df[filtro_salidas], use_container_width=True)

    with tab4:
        st.dataframe(df, use_container_width=True)

else:
    st.info("👋 Aún no hay datos. Registra tu primera operación arriba.")
