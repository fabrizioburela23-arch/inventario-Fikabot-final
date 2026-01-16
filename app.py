import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Inventario AI", layout="wide", page_icon="📦")

# Estilos CSS para que se vea moderno (similar a tu diseño original)
st.markdown("""
<style>
    .stApp { background-color: #0f172a; color: #e2e8f0; }
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] { 
        background-color: #1e293b !important; color: #ffffff !important; 
    }
    div[data-testid="stMetricValue"] { color: #10b981; } /* Color verde esmeralda */
</style>
""", unsafe_allow_html=True)

# --- TÍTULO ---
col_header_1, col_header_2 = st.columns([3, 1])
with col_header_1:
    st.title("📦 Inventario AI Centralizado")
with col_header_2:
    st.write(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y')}")

# --- MEMORIA TEMPORAL (Antes de conectar Google Sheets) ---
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Fecha", "Descripción", "Lote", "Cantidad", "Unidad", 
        "Movimiento", "Origen/Destino", "Costo Unitario", "Costo Total", "Observaciones"
    ])

# --- BARRA LATERAL ---
with st.sidebar:
    st.header("Opciones")
    st.info("💡 Tip: Pronto conectaremos esto a Google Sheets para que los datos se guarden para siempre.")
    if st.button("🗑️ Borrar todos los datos (Reset)"):
        st.session_state.data = st.session_state.data.iloc[0:0]
        st.rerun()

# --- FORMULARIO DE INGRESO ---
with st.expander("📝 Ingreso de Movimientos", expanded=True):
    # Fila 1 de inputs
    c1, c2, c3, c4 = st.columns(4)
    desc = c1.text_input("Descripción (Ej: Tomate)")
    lote = c2.text_input("Lote (Ej: INT-001)", value="GEN-001")
    cant = c3.number_input("Cantidad", min_value=0.0, format="%.2f")
    unidad = c4.selectbox("Unidad", ["kg", "ud", "litros", "cajas"])
    
    # Fila 2 de inputs
    c5, c6, c7, c8 = st.columns(4)
    mov = c5.selectbox("Tipo Movimiento", ["Entrada", "Salida", "Inv. Inicial"])
    origen = c6.text_input("Origen/Destino", value="Proveedor General")
    costo = c7.number_input("Costo Unitario (Bs)", min_value=0.0, format="%.2f")
    obs = c8.text_input("Observaciones")

    # Botón de guardar
    if st.button("Registrar Movimiento", type="primary", use_container_width=True):
        if desc and cant > 0:
            nuevo_registro = {
                "Fecha": datetime.now().strftime("%Y-%m-%d"),
                "Descripción": desc,
                "Lote": lote,
                "Cantidad": cant,
                "Unidad": unidad,
                "Movimiento": mov,
                "Origen/Destino": origen,
                "Costo Unitario": costo,
                "Costo Total": cant * costo,
                "Observaciones": obs
            }
            # Añadir a la tabla
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([nuevo_registro])], 
                ignore_index=True
            )
            st.success("✅ ¡Movimiento registrado!")
        else:
            st.warning("⚠️ Por favor ingresa al menos una descripción y cantidad.")

# --- TABLA Y CÁLCULOS ---
st.divider()
df = st.session_state.data

if not df.empty:
    # Cálculos simples
    entradas = df[df['Movimiento'].isin(['Entrada', 'Inv. Inicial'])]['Cantidad'].sum()
    salidas = df[df['Movimiento'] == 'Salida']['Cantidad'].sum()
    stock_actual = entradas - salidas
    valor_inventario = df['Costo Total'].sum() # Simplificado (Entradas - Salidas en dinero requiere lógica FIFO/Promedio, por ahora suma bruta)

    # Métricas
    m1, m2, m3 = st.columns(3)
    m1.metric("📦 Stock Total (Unidades)", f"{stock_actual:,.2f}")
    m2.metric("💰 Valor Estimado", f"Bs {valor_inventario:,.2f}")
    m3.metric("📄 Total Registros", len(df))

    # Mostrar Tabla
    st.subheader("📋 Detalle de Movimientos")
    st.dataframe(df, use_container_width=True)
else:
    st.info("👋 La tabla está vacía. Añade tu primer producto arriba.")
