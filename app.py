from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Mi Control de Paquetes", page_icon="📦", layout="centered"
)

# Estilo CSS para replicar el diseño de tarjeta limpia y botones horizontales idénticos a la referencia
st.markdown(
    """
    <style>
    /* Ocultar el menú superior predeterminado de Streamlit y la barra de navegación de pestañas */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Contenedor tipo tarjeta similar a la app */
    .paquete-card {
        background-color: #1e1e1e;
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #333;
    }
    
    /* Forzar que los botones de acción queden estrictamente horizontal y compactos */
    div.row-widget.stHorizontal {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    div.row-widget.stHorizontal > div {
        flex: 1;
    }
    
    /* Estética de los botones para que se parezcan a la imagen */
    div.stButton > button {
        border-radius: 8px;
        font-size: 13px;
        padding: 6px 10px;
        width: 100%;
        background-color: #2b2b2b;
        color: white;
        border: 1px solid #444;
    }
    div.stButton > button:hover {
        background-color: #3b3b3b;
        border-color: #666;
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


# Estado de navegación inferior (simulando la barra de la app)
if "menu_actual" not in st.session_state:
  st.session_state["menu_actual"] = "Paquetes"

# Título principal limpio
st.markdown(
    "<h2 style='text-align: center; color: #fff; margin-bottom: 20px;'>📦"
    " Biagio Cargo</h2>",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# 1. SECCIÓN: REGISTRAR (Menú Formulario)
# ---------------------------------------------------------
if st.session_state["menu_actual"] == "Registrar":
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
        st.success("¡Orden registrada con éxito!")


# ---------------------------------------------------------
# 2. SECCIÓN: PAQUETES (Filtros por Estado estilo Pestañas)
# ---------------------------------------------------------
elif st.session_state["menu_actual"] == "Paquetes":
  # Sub-pestallas de estados de paquetes
  sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
      "⏳ En Espera",
      "🏢 En Casillero",
      "🚢 En Camino",
      "✅ Entregados",
  ])


  def mostrar_pestana(estado_filtro):
    df_actual = cargar_datos()

    busqueda = st.text_input(
        "🔍 Buscar guía o track...", key=f"search_{estado_filtro}"
    )

    filtrados = df_actual[df_actual["estado"] == estado_filtro]
    if busqueda:
      filtrados = filtrados[
          filtrados["tracking"].str.contains(busqueda, case=False, na=False)
      ]

    st.write(f"**Total en esta sección:** {len(filtrados)}")

    if filtrados.empty:
      st.info("No hay paquetes registrados aquí.")
      return

    for index, row in filtrados.iterrows():
      # Tarjeta limpia idéntica al diseño de la app de referencia
      st.markdown(
          f"""
            <div class="paquete-card">
                📦 <b>{row['tracking']}</b><br>
                <span style="background-color: #332211; color: #ffaa55; padding: 2px 8px; border-radius: 4px; font-size: 11px;">🚚 {estado_filtro}</span><br>
                <span style="color: #aaa; font-size: 13px;">Descripción: {row['descripcion']}</span><br>
                <span style="color: #aaa; font-size: 13px;">💰 Monto: ${row['monto']} | 📅 Fecha: {row['fecha']}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

      # Botones principales uno al lado del otro exactamente como "Ver Detalles" e "Imprimir factura"
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
          if st.button("✅ Entregado", key=f"c5_{index}"):
            df_actual.at[index, "estado"] = "Entregados"
            guardar_datos(df_actual)
            st.rerun()

      elif estado_filtro == "Entregados":
        with col1:
          if st.button("🗑️ Eliminar", key=f"del2_{index}"):
            df_actual = df_actual.drop(index)
            guardar_datos(df_actual)
            st.rerun()

  with sub_tab1:
    mostrar_pestana("En Espera")
  with sub_tab2:
    mostrar_pestana("En Casillero")
  with sub_tab3:
    mostrar_pestana("En Camino")
  with sub_tab4:
    mostrar_pestana("Entregados")


# ---------------------------------------------------------
# 3. SECCIÓN: DIRECCIONES
# ---------------------------------------------------------
elif st.session_state["menu_actual"] == "Direcciones":
  st.subheader("🏢 Direcciones de Casillero")
  st.info("Aquí puedes ver las direcciones de envío en China y Miami.")


# ---------------------------------------------------------
# 4. SECCIÓN: PERFIL
# ---------------------------------------------------------
elif st.session_state["menu_actual"] == "Perfil":
  st.subheader("👤 Mi Perfil")
  st.write("Configuración de cuenta y datos personales.")


# ---------------------------------------------------------
# BARRA DE NAVEGACIÓN INFERIOR (Estilo App Móvil)
# ---------------------------------------------------------
st.markdown("<br><hr style='border-color: #444;'>", unsafe_allow_html=True)

# Creamos columnas abajo para simular los iconos de la barra inferior de la imagen de referencia
b1, b2, b3, b4 = st.columns(4)

with b1:
  if st.button("➕ Registrar", use_container_width=True):
    st.session_state["menu_actual"] = "Registrar"
    st.rerun()

with b2:
  if st.button("📦 Paquetes", use_container_width=True):
    st.session_state["menu_actual"] = "Paquetes"
    st.rerun()

with b3:
  if st.button("🏢 Direcciones", use_container_width=True):
    st.session_state["menu_actual"] = "Direcciones"
    st.rerun()

with b4:
  if st.button("👤 Perfil", use_container_width=True):
    st.session_state["menu_actual"] = "Perfil"
    st.rerun()
