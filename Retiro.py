import streamlit as st
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(page_title="Calculadora de Interés Compuesto", page_icon="📈", layout="centered")

# --- Función de Cálculo Principal ---
def calcular_crecimiento_anual(tasa_anual, monto_inicial, tramos, frecuencia_str):
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
    
    # Tasa efectiva del periodo (absorbe la capitalización diaria)
    tasa_efectiva_periodo = (1 + tasa_diaria)**dias_por_periodo - 1
    
    datos = []
    balance_actual = monto_inicial
    total_invertido = monto_inicial
    ano_actual = 1
    
    # Iteramos sobre cada etapa definida por el usuario
    for tramo in tramos:
        anos_tramo = tramo["anos"]
        aportacion_tramo = tramo["aportacion"]
        
        for _ in range(int(anos_tramo)):
            # 1. El dinero que ya estaba en la cuenta crece todo el año con capitalización diaria
            balance_actual = balance_actual * (1 + tasa_diaria)**365
            
            # 2. Las aportaciones nuevas de este año crecen según su frecuencia
            if aportacion_tramo > 0:
                nuevo_valor_depositos = aportacion_tramo * (((1 + tasa_efectiva_periodo)**depositos_por_ano - 1) / tasa_efectiva_periodo)
                balance_actual += nuevo_valor_depositos
                total_invertido += (aportacion_tramo * depositos_por_ano)
            
            # Guardamos el registro del año para la tabla/gráfica
            datos.append({
                "Año": ano_actual,
                "Aportación Anual": aportacion_tramo * depositos_por_ano,
                "Total Invertido": round(total_invertido, 2),
                "Intereses Acumulados": round(balance_actual - total_invertido, 2),
                "Balance Total": round(balance_actual, 2)
            })
            ano_actual += 1
            
    return pd.DataFrame(datos), balance_actual, total_invertido

# --- Interfaz de Usuario (UI) ---
st.title("📈 Calculadora Avanzada de Interés Compuesto")
st.write("Modela tu crecimiento financiero con capitalización diaria y ajusta tus aportaciones a lo largo del tiempo.")

# --- Menú Lateral (Sidebar) ---
st.sidebar.header("Parámetros Generales")

monto_inicial = st.sidebar.number_input("Monto Inicial ($):", min_value=0.0, value=0.0, step=1000.0)
anos_totales = st.sidebar.slider("Años totales de inversión:", min_value=1, max_value=50, value=40, step=1)
tasa_anual_porcentaje = st.sidebar.slider("Tasa de interés anual (%):", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
frecuencia_str = st.sidebar.selectbox("Frecuencia de aportación:", ["Diaria", "Semanal", "Quincenal", "Mensual", "Anual"], index=2)

st.sidebar.divider()

# --- Lógica de Configuración Avanzada ---
avanzado = st.sidebar.checkbox("⚙️ Configuración Avanzada (Desglosar por etapas)")

tramos = [] # Aquí guardaremos los años y montos de cada etapa
error_en_anos = False

if avanzado:
    st.sidebar.write(f"**Años a distribuir:** {anos_totales}")
    num_tramos = st.sidebar.number_input("¿En cuántas etapas dividirás tu inversión?", min_value=1, max_value=10, value=2, step=1)
    
    anos_acumulados = 0
    for i in range(int(num_tramos)):
        with st.sidebar.expander(f"Etapa {i+1}", expanded=True):
            # Para la última etapa, sugerimos los años restantes por defecto
            if i == num_tramos - 1:
                anos_restantes = max(1, anos_totales - anos_acumulados)
                anos_tramo = st.number_input(f"Años", min_value=1, value=int(anos_restantes), key=f"ano_{i}")
            else:
                anos_tramo = st.number_input(f"Años", min_value=1, value=10, key=f"ano_{i}")
            
            aportacion_tramo = st.number_input(f"Aportación {frecuencia_str.lower()} ($)", min_value=0.0, value=5000.0, step=500.0, key=f"aport_{i}")
            
            tramos.append({"anos": anos_tramo, "aportacion": aportacion_tramo})
            anos_acumulados += anos_tramo
            
    # Validación dinámica
    if anos_acumulados != anos_totales:
        st.sidebar.error(f"⚠️ La suma de las etapas ({anos_acumulados} años) no coincide con el total de años ({anos_totales}).")
        error_en_anos = True
else:
    # Si no es avanzado, es un solo tramo que dura todos los años
    deposito_unico = st.sidebar.number_input(f"Cantidad de aportación {frecuencia_str.lower()} ($):", min_value=0.0, value=5000.0, step=500.0)
    tramos = [{"anos": anos_totales, "aportacion": deposito_unico}]

# --- Ejecución y Resultados ---
tasa_anual_decimal = tasa_anual_porcentaje / 100

if st.button("Calcular Proyección", type="primary"):
    if error_en_anos:
        st.error("Por favor, corrige los años en la configuración avanzada para que sumen exactamente el total de la inversión.")
    else:
        df_resultados, balance_final, invertido_final = calcular_crecimiento_anual(
            tasa_anual_decimal, monto_inicial, tramos, frecuencia_str
        )
        
        intereses_totales = balance_final - invertido_final
        
        # --- Mostrar Métricas ---
        col1, col2, col3 = st.columns(3)
        col1.metric("Capital Invertido", f"${invertido_final:,.2f}")
        col2.metric("Intereses Ganados", f"${intereses_totales:,.2f}")
        col3.metric("Balance Final", f"${balance_final:,.2f}")
        
        st.divider()
        
        # --- Gráfica ---
        st.subheader("Evolución de tu Capital")
        df_grafica = df_resultados.set_index("Año")[["Total Invertido", "Intereses Acumulados"]]
        st.area_chart(df_grafica)
        
        # --- Tabla de Amortización ---
        st.subheader("Desglose Año por Año")
        st.dataframe(
            df_resultados.set_index("Año").style.format({
                "Aportación Anual": "${:,.2f}",
                "Total Invertido": "${:,.2f}",
                "Intereses Acumulados": "${:,.2f}",
                "Balance Total": "${:,.2f}"
            }), 
            use_container_width=True
        )
