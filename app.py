from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Mi Control de Paquetes", page_icon="📦", layout="centered"
)

# Estilo CSS para forzar que las columnas de botones se queden de lado a lado en celulares
st.markdown(
    """
    <style>
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        gap: 10px !important;
    }
    [data-testid="stHorizontalBlock"] > div {
        flex: 1 !important;
        min-width: unset !important;
    }
    .stButton > button {
        width: 100% !important;
        padding: 4px 6px !important;
        font-size: 13px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

EXCEL_FILE = "mis_paquetes_simple.csv"


# Cargar datos
def cargar_datos():
  if os.path.exists(EXCEL_FILE):
    df = pd.read_csv(EXCEL_FILE)
    columnas_necesarias = ["tracking", "descripcion", "monto", "fecha", "estado"]
    for col in columnas_necesarias:
      if col not in df.columns:
        df[col] = ""
    return df
  else:
    return pd.DataFrame(
        columns=["tracking", "descripcion", "monto", "fecha", "estado"]
    )


# Guardar datos
def guardar_datos(df_guardar):
  df_guardar.to_csv(EXCEL_FILE, index=False)


# Inicializar variable de estado para los mensajes de éxito
if "mensaje_exito" not in st.session_state:
  st.session_state.mensaje_exito = ""

# Título principal
st.markdown(
    "<h2 style='text-align: center; color: #fff;'>📦 MI CONTROL DE"
    " PAQUETES</h2>",
    unsafe_allow_html=True,
)

# Pestañas originales de navegación arriba (4 pestañas originales)
tab1, tab2, tab3, tab4 = st.tabs(
    ["➕ Registrar", "⏳ En Espera", "🏢 En Casillero", "🚢 En Camino"]
)


# ---------------------------------------------------------
# 1. REGISTRAR ORDEN
# ---------------------------------------------------------
with tab1:
  st.subheader("Registrar Nueva Orden (1688)")

  # Mostrar el mensaje de éxito guardado en la sesión (si existe) y luego limpiarlo
  if st.session_state.mensaje_exito:
    st.success(st.session_state.mensaje_exito)
    st.session_state.mensaje_exito = ""

  with st.form("form_registro", clear_on_submit=True):
    tracking = st.text_input("Número de Tracking / Guía de 1688 *")
    descripcion = st.text_input(
        "Descripción de lo que viene *",
        placeholder="Ej: Ropa deportiva, accesorios, etc.",
    )
    monto = st.text_input("Monto Pagado ($)", placeholder="Ej: 9 o 15.50")

    enviar = st.form_submit_button("Guardar Orden")

    if enviar:
      if not tracking or not descripcion:
        st.warning(
            "Por favor, completa al menos el Tracking y la Descripción."
        )
      else:
        df_actual = cargar_datos()

        # Validar si el tracking ya existe (ignorando espacios y mayúsculas/minúsculas)
        tracking_limpio = tracking.strip().lower()
        existente = False
        if not df_actual.empty:
          existente = (
              df_actual["tracking"]
              .astype(str)
              .str.strip()
              .str.lower()
              .isin([tracking_limpio])
              .any()
          )

        if existente:
          st.error(
              "⚠️ ¡Este número de tracking ya fue registrado! Por favor,"
              " verifícalo."
          )
        else:
          nueva_fila = pd.DataFrame({
              "tracking": [tracking.strip()],
              "descripcion": [descripcion.strip()],
              "monto": [monto.strip()],
              "fecha": [datetime.now().strftime("%d/%m/%Y")],
              "estado": ["En Espera"],
          })

          df_actual = pd.concat([df_actual, nueva_fila], ignore_index=True)
          guardar_datos(df_actual)

          # Guardar en el estado para que aparezca limpio y no persista al volver
          st.session_state.mensaje_exito = (
              "¡Orden registrada con éxito! Ya aparecerá en 'En Espera'."
          )
          st.rerun()


# ---------------------------------------------------------
# FUNCION PARA MOSTRAR TARJETAS Y BOTONES
# ---------------------------------------------------------
def mostrar_pestana(estado_filtro):
  df_actual = cargar_datos()

  busqueda = st.text_input(
      "🔍 Buscar tracking...", key=f"search_{estado_filtro}"
  )

  filtrados = df_actual[df_actual["estado"] == estado_filtro]
  if busqueda:
    filtrados = filtrados[
        filtrados["tracking"].str.contains(busqueda, case=False, na=False)
    ]

  st.write(f"**Total:** {len(filtrados)}")

  if filtrados.empty:
    st.info("No hay paquetes en esta sección.")
    return

  for index, row in filtrados.iterrows():
    with st.container():
      st.markdown(
          f"""
            <div style="background-color: #1e1e1e; padding: 10px 14px; border-radius: 6px; margin-bottom: 6px;">
                📌 <b>Tracking:</b> {row['tracking']} | 📝 <b>Desc:</b> {row['descripcion']}<br>
                💰 <b>Monto:</b> ${row['monto']} | 📅 <b>Fecha:</b> {row['fecha']}
            </div>
            """,
          unsafe_allow_html=True,
      )

      # Botones de acción uno al lado del otro
      col1, col2 = st.columns(2)

      if estado_filtro == "En Espera":
        with col1:
          if st.button("🏢 Al casillero", key=f"c1_{index}"):
            df_actual.at[index, "estado"] = "En Casillero"
            guardar_datos(df_actual)
            st.rerun()
        with col2:
          if st.button("🗑️ Eliminar", key=f"del_{index}"):
            df_actual = df_actual.drop(index)
            guardar_datos(df_actual)
            st.rerun()

      elif estado_filtro == "En Casillero":
        with col1:
          if st.button("🔄 Devolver", key=f"c2_{index}"):
            df_actual.at[index, "estado"] = "En Espera"
            guardar_datos(df_actual)
            st.rerun()
        with col2:
          if st.button("🚢 En Camino", key=f"c3_{index}"):
            df_actual.at[index, "estado"] = "En Camino"
            guardar_datos(df_actual)
            st.rerun()

      elif estado_filtro == "En Camino":
        with col1:
          if st.button("🔄 Devolver", key=f"c4_{index}"):
            df_actual.at[index, "estado"] = "En Casillero"
            guardar_datos(df_actual)
            st.rerun()
        with col2:
          if st.button("✅ En Mis Manos", key=f"c5_{index}"):
            df_actual = df_actual.drop(index)
            guardar_datos(df_actual)
            st.rerun()


# ---------------------------------------------------------
# 2. VISTAS EN PESTAÑAS
# ---------------------------------------------------------
with tab2:
  st.subheader("Paquetes En Espera")
  mostrar_pestana("En Espera")

with tab3:
  st.subheader("Paquetes En Casillero")
  mostrar_pestana("En Casillero")

with tab4:
  st.subheader("Paquetes En Camino")
  mostrar_pestana("En Camino")
