from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Biagio Cargo", page_icon="📦", layout="centered"
)

# Estilo CSS avanzado para la barra inferior fija, tarjetas limpias y botones en línea
st.markdown(
    """
    <style>
    /* Ocultar elementos nativos molestos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Estética general de la tarjeta de paquetes */
    .paquete-card {
        background-color: #1e1e1e;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #333;
    }
    
    /* Forzar que los botones de las tarjetas queden estrictamente horizontal y pequeños */
    div.row-widget.stHorizontal {
        display: flex;
        gap: 8px;
    }
    div.row-widget.stHorizontal > div {
        flex: 1;
    }
    div.stButton > button {
        border-radius: 6px;
        font-size: 12px;
        padding: 4px 8px;
        width: 100%;
        background-color: #2b2b2b;
        color: white;
        border: 1px solid #444;
    }
    
    /* Espaciado para que el contenido no quede tapado por la barra inferior */
    .block-container {
        padding-bottom: 90px;
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


# Control de la sección actual mediante Session State
if "seccion_activa" not in st.session_state:
  st.session_state["seccion_activa"] = "Inicio"

# Encabezado principal
st.markdown(
    "<h2 style='text-align: center; color: #fff; margin-bottom: 15px;'>📦"
    " Biagio Cargo</h2>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# SECCIÓN 1: INICIO (Resumen estilo app de referencia)
# ---------------------------------------------------------
if st.session_state["seccion_activa"] == "Inicio":
  df_resumen = cargar_datos()
  total_paquetes = len(df_resumen)
  en_transito = len(df_resumen[df_resumen["estado"] == "En Camino"])
  entregados = len(df_resumen[df_resumen["estado"] == "Entregados"])

  st.markdown("### 📊 Resumen de cuenta")

  col_a, col_b = st.columns(2)
  with col_a:
    st.markdown(
        f"""
        <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #333;">
            <h3 style="color: #ffaa55; margin: 0;">{en_transito}</h3>
            <p style="color: #aaa; margin: 0; font-size: 13px;">EN TRÁNSITO</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
  with col_b:
    st.markdown(
        f"""
        <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; text-align: center; border: 1px solid #333;">
            <h3 style="color: #55ff55; margin: 0;">{entregados}</h3>
            <p style="color: #aaa; margin: 0; font-size: 13px;">ENTREGADOS</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

  st.markdown("<br>", unsafe_allow_html=True)
  st.markdown(
      f"""
    <div style="background-color: #1e1e1e; padding: 15px; border-radius: 10px; border: 1px solid #333;">
        <h4 style="margin: 0; color: #fff;">📦 Total Registrados: {total_paquetes}</h4>
        <p style="color: #aaa; font-size: 12px; margin: 5px 0 0 0;">Envíos registrados en tu cuenta listos para gestionar.</p>
    </div>
    """,
      unsafe_allow_html=True,
  )


# ---------------------------------------------------------
# SECCIÓN 2: PAQUETES (Filtro por estados con botones laterales)
# ---------------------------------------------------------
elif st.session_state["seccion_activa"] == "Paquetes":
  # Selector limpio de estados en lugar de pestañas feas
  estado_seleccionado = st.selectbox(
      "Filtrar por estado",
      ["En Espera", "En Casillero", "En Camino", "Entregados"],
  )

  df_actual = cargar_datos()
  busqueda = st.text_input("🔍 Buscar guía o track...")

  filtrados = df_actual[df_actual["estado"] == estado_seleccionado]
  if busqueda:
    filtrados = filtrados[
        filtrados["tracking"].str.contains(busqueda, case=False, na=False)
    ]

  st.write(f"**Total encontrados:** {len(filtrados)}")

  if filtrados.empty:
    st.info("No hay paquetes registrados en este estado.")
  else:
    for index, row in filtrados.iterrows():
      st.markdown(
          f"""
            <div class="paquete-card">
                📌 <b>Guía:</b> {row['tracking']}<br>
                📝 <b>Descripción:</b> {row['descripcion']}<br>
                💰 <b>Monto:</b> ${row['monto']} | 📅 <b>Fecha:</b> {row['fecha']}
            </div>
            """,
          unsafe_allow_html=True,
      )

      # Botones de acción estrictamente uno al lado del otro
      col1, col2 = st.columns(2)

      if estado_seleccionado == "En Espera":
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

      elif estado_seleccionado == "En Casillero":
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

      elif estado_seleccionado == "En Camino":
        with col1:
          if st.button("🔄 Devolver", key=f"c4_{index}"):
            df_actual.at[index, "estado"] = "En Casillero"
            guardar_datos(df_actual)
            st.rerun()
        with col2:
          if st.button("✅ Entregado", key=f"c5_{index}"):
            df_actual.at[index, "estado"] = "Entregados"
            guardar_datos(df_actual)
            st.rerun()

      elif estado_seleccionado == "Entregados":
        with col1:
          if st.button("🗑️ Eliminar", key=f"del2_{index}"):
            df_actual = df_actual.drop(index)
            guardar_datos(df_actual)
            st.rerun()


# ---------------------------------------------------------
# SECCIÓN 3: REGISTRAR (Formulario de carga)
# ---------------------------------------------------------
elif st.session_state["seccion_activa"] == "Registrar":
  st.subheader("➕ Registrar Nueva Orden")

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
        nueva_fila = pd.DataFrame({
            "tracking": [tracking.strip()],
            "descripcion": [descripcion.strip()],
            "monto": [monto.strip()],
            "fecha": [datetime.now().strftime("%d/%m/%Y")],
            "estado": ["En Espera"],
        })

        df_actual = pd.concat([df_actual, nueva_fila], ignore_index=True)
        guardar_datos(df_actual)
        st.success(
            "¡Orden registrada con éxito! Ya aparecerá en Paquetes (En"
            " Espera)."
        )


# ---------------------------------------------------------
# SECCIÓN 4: DIRECCIONES Y PERFIL
# ---------------------------------------------------------
elif st.session_state["seccion_activa"] == "Direcciones":
  st.subheader("🏢 Direcciones de Casillero")
  st.info(
      "Consulta aquí las direcciones de recepción en China y Miami para tus"
      " compras de 1688."
  )

elif st.session_state["seccion_activa"] == "Perfil":
  st.subheader("👤 Mi Perfil")
  st.write("Configuración de tu cuenta y datos de usuario.")


# ---------------------------------------------------------
# BARRA DE NAVEGACIÓN INFERIOR (Estilo App Móvil Idéntica)
# ---------------------------------------------------------
st.markdown(
    """
    <style>
    .nav-bar-mobile {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #121212;
        border-top: 1px solid #333;
        display: flex;
        justify-content: space-around;
        padding: 8px 0;
        z-index: 99999;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Botones inferiores interactivos distribuidos de forma idéntica a una app real
col_n1, col_n2, col_n3, col_n4, col_n5 = st.columns(5)

with col_n1:
  if st.button("🏠 Inicio", use_container_width=True):
    st.session_state["seccion_activa"] = "Inicio"
    st.rerun()

with col_n2:
  if st.button("📦 Paquetes", use_container_width=True):
    st.session_state["seccion_activa"] = "Paquetes"
    st.rerun()

with col_n3:
  if st.button("➕ Registrar", use_container_width=True):
    st.session_state["seccion_activa"] = "Registrar"
    st.rerun()

with col_n4:
  if st.button("🏢 Direcciones", use_container_width=True):
    st.session_state["seccion_activa"] = "Direcciones"
    st.rerun()

with col_n5:
  if st.button("👤 Perfil", use_container_width=True):
    st.session_state["seccion_activa"] = "Perfil"
    st.rerun()
