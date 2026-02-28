import streamlit as st
import pandas as pd

# --- Configuración de la página ---
st.set_page_config(page_title="Calculadora de Interés Compuesto", page_icon="📈", layout="centered")

# --- Función de Cálculo (Motor Financiero) ---
def calcular_proyeccion(tasa_anual, monto_inicial, tramos, frecuencia_str):
    """
    Calcula la proyección financiera iterando sobre una lista de 'tramos'.
    Cada tramo tiene una duración en años y una aportación específica.
    """
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
    
    # Iteramos sobre cada tramo definido (sea 1 en modo simple o N en avanzado)
    for tramo in tramos:
        duracion_tramo = int(tramo["anos"])
        aportacion_tramo = tramo["aportacion"]
        
        for _ in range(duracion_tramo):
            # 1. El capital acumulado crece con capitalización diaria todo el año
            balance_actual = balance_actual * (1 + tasa_diaria)**365
            
            # 2. Se suman las nuevas aportaciones del año (con sus rendimientos intra-anuales)
            if aportacion_tramo > 0:
                nuevo_valor_depositos = aportacion_tramo * (((1 + tasa_efectiva_periodo)**depositos_por_ano - 1) / tasa_efectiva_periodo)
                balance_actual += nuevo_valor_depositos
                total_invertido += (aportacion_tramo * depositos_por_ano)
            
            # Guardamos el registro
            datos.append({
                "Año": ano_actual,
                "Aportación Mensual/Quincenal/etc": aportacion_tramo,
                "Total Invertido (Bolsillo)": round(total_invertido, 2),
                "Intereses Ganados": round(balance_actual - total_invertido, 2),
                "Balance Total": round(balance_actual, 2)
            })
            ano_actual += 1
            
    return pd.DataFrame(datos), balance_actual, total_invertido

# --- Interfaz de Usuario (UI) ---
st.title("📈 Proyección de Interés Compuesto")

# --- BARRA LATERAL (Inputs) ---
st.sidebar.header("Parámetros Generales")

# 1. Variables Comunes (siempre visibles)
monto_inicial = st.sidebar.number_input("Monto Inicial ($):", min_value=0.0, value=10000.0, step=1000.0)
anos_totales = st.sidebar.slider("Duración Total (Años):", min_value=1, max_value=60, value=30)
tasa_anual_pct = st.sidebar.number_input("Tasa Anual Esperada (%):", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
frecuencia = st.sidebar.selectbox("Frecuencia de Aportación:", ["Mensual", "Quincenal", "Semanal", "Diaria", "Anual"], index=0)

st.sidebar.markdown("---")

# 2. Selector de Modo
modo_avanzado = st.sidebar.checkbox("🛠️ Configuración Avanzada (Etapas variables)")

tramos = []
error_config = False

if not modo_avanzado:
    # --- MODO SIMPLE ---
    st.sidebar.subheader("Configuración Simple")
    aportacion_simple = st.sidebar.number_input(f"Aportación {frecuencia.lower()} constante ($):", min_value=0.0, value=2000.0, step=100.0)
    
    # Creamos un único tramo que dura todo el periodo
    tramos.append({
        "anos": anos_totales, 
        "aportacion": aportacion_simple
    })

else:
    # --- MODO AVANZADO ---
    st.sidebar.subheader("Desglose por Etapas")
    st.sidebar.info(f"Debes distribuir los {anos_totales} años totales en diferentes etapas.")
    
    num_etapas = st.sidebar.number_input("Número de etapas:", min_value=1, max_value=10, value=2)
    
    anos_asignados = 0
    
    for i in range(int(num_etapas)):
        st.sidebar.markdown(f"**Etapa {i+1}**")
        
        # Sugerir años restantes para la última etapa
        default_anos = 5
        if i == num_etapas - 1:
            default_anos = max(1, anos_totales - anos_asignados)
            
        a_tramo = st.sidebar.number_input(f"Duración (años) - Etapa {i+1}", min_value=1, value=int(default_anos), key=f"a_{i}")
        p_tramo = st.sidebar.number_input(f"Aportación {frecuencia.lower()} ($) - Etapa {i+1}", min_value=0.0, value=0.0, step=500.0, key=f"p_{i}")
        
        tramos.append({"anos": a_tramo, "aportacion": p_tramo})
        anos_asignados += a_tramo
    
    # Validación de años
    if anos_asignados != anos_totales:
        st.error(f"⚠️ Error en tiempos: Tus etapas suman {anos_asignados} años, pero definiste un total de {anos_totales} años arriba. Ajusta las etapas.")
        error_config = True

# --- BOTÓN DE CÁLCULO ---
if st.button("Calcular Proyección", type="primary"):
    
    if error_config:
        st.warning("Por favor corrige la suma de años en la configuración avanzada para continuar.")
    else:
        # Convertir tasa a decimal
        tasa_decimal = tasa_anual_pct / 100
        
        # Ejecutar cálculo
        df, final, invertido = calcular_proyeccion(tasa_decimal, monto_inicial, tramos, frecuencia)
        ganancia = final - invertido
        
        # --- RESULTADOS ---
        st.markdown("### Resumen Financiero")
        c1, c2, c3 = st.columns(3)
        c1.metric("Dinero de tu bolsillo", f"${invertido:,.2f}")
        c2.metric("Intereses Generados", f"${ganancia:,.2f}", delta="Ganancia")
        c3.metric("Monto Final Total", f"${final:,.2f}")
        
        st.divider()
        
        # Gráfica de Área
        st.subheader("Trayectoria del Patrimonio")
        st.area_chart(df.set_index("Año")[["Total Invertido (Bolsillo)", "Intereses Ganados"]])
        
        # Tabla detallada
        with st.expander("Ver tabla de datos detallada"):
            st.dataframe(
                df.style.format({
                    "Total Invertido (Bolsillo)": "${:,.2f}", 
                    "Intereses Ganados": "${:,.2f}", 
                    "Balance Total": "${:,.2f}",
                    "Aportación Mensual/Quincenal/etc": "${:,.2f}"
                })
    )
        
