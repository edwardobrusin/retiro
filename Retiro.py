import streamlit as st
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(page_title="Calculadora de Interés Compuesto", page_icon="📈", layout="centered")

# --- Funciones de Cálculo ---
def calcular_crecimiento_anual(tasa_anual, deposito_periodico, frecuencia_str, anos):
    frecuencias = {
        "Diaria": 365,
        "Semanal": 52,
        "Quincenal": 24,
        "Mensual": 12,
        "Anual": 1
    }
    depositos_por_ano = frecuencias[frecuencia_str]
    tasa_diaria = tasa_anual / 365
    dias_por_periodo = 365 / depositos_por_ano
    tasa_efectiva_periodo = (1 + tasa_diaria)**dias_por_periodo - 1
    
    datos = []
    balance_actual = 0
    total_invertido = 0
    
    # Proyección año por año para la gráfica
    for ano in range(1, int(anos) + 1):
        # El balance del año anterior crece con capitalización diaria todo este año
        balance_actual = balance_actual * (1 + tasa_diaria)**365
        
        # Los nuevos depósitos de este año crecen según la tasa efectiva del periodo
        nuevo_valor_depositos = deposito_periodico * (((1 + tasa_efectiva_periodo)**depositos_por_ano - 1) / tasa_efectiva_periodo)
        
        balance_actual += nuevo_valor_depositos
        total_invertido += (deposito_periodico * depositos_por_ano)
        
        datos.append({
            "Año": ano,
            "Total Invertido": round(total_invertido, 2),
            "Intereses Acumulados": round(balance_actual - total_invertido, 2),
            "Balance Total": round(balance_actual, 2)
        })
        
    return pd.DataFrame(datos), balance_actual, total_invertido

# --- Interfaz de Usuario (UI) ---
st.title("📈 Calculadora de Interés Compuesto")
st.write("Descubre cuánto puede crecer tu dinero en el tiempo gracias a la capitalización diaria y tus aportaciones periódicas.")

st.sidebar.header("Tus Variables")

# Entradas de usuario
deposito_periodico = st.sidebar.number_input("Cantidad de aportación ($):", min_value=0.0, value=5000.0, step=500.0)
frecuencia_str = st.sidebar.selectbox("Frecuencia de aportación:", ["Diaria", "Semanal", "Quincenal", "Mensual", "Anual"], index=2)
tasa_anual_porcentaje = st.sidebar.slider("Tasa de interés anual (%):", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
anos = st.sidebar.slider("Años de inversión:", min_value=1, max_value=50, value=40, step=1)

# Procesamiento
tasa_anual_decimal = tasa_anual_porcentaje / 100

if st.sidebar.button("Calcular"):
    df_resultados, balance_final, invertido_final = calcular_crecimiento_anual(
        tasa_anual_decimal, deposito_periodico, frecuencia_str, anos
    )
    
    intereses_totales = balance_final - invertido_final
    
    # --- Mostrar Métricas Principales ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Aportación Total", f"${invertido_final:,.2f}")
    col2.metric("Intereses Ganados", f"${intereses_totales:,.2f}")
    col3.metric("Balance Final", f"${balance_final:,.2f}")
    
    st.divider()
    
    # --- Gráfica ---
    st.subheader("Crecimiento de tu Inversión en el Tiempo")
    # Preparamos los datos para que el área chart muestre el desglose claramente
    df_grafica = df_resultados.set_index("Año")[["Total Invertido", "Intereses Acumulados"]]
    st.area_chart(df_grafica)
    
    # --- Tabla de Amortización (Opcional) ---
    with st.expander("Ver tabla de crecimiento año por año"):
        st.dataframe(df_resultados.set_index("Año"), use_container_width=True)
else:
    st.info("Ajusta las variables en el menú lateral y presiona 'Calcular' para ver la proyección.")
