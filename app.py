from datetime import datetime
import os
import pandas as pd
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Mi Control de Paquetes", page_icon="📦", layout="centered"
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
def guardar_datos(df):
  df.to_csv(EXCEL_FILE, index=False)


df = cargar_datos()

# Título principal limpio
st.markdown(
    "<h3 style='text-align: center; color: #fff; margin-bottom: 20px;'>📦 MI"
    " CONTROL DE PAQUETES</h3>",
    unsafe_allow_html=True,
)

# Menú de navegación horizontal compacto
menu = [
    "➕ Registrar",
    "⏳ Espera",
    "🏢 Casillero",
    "🚢 Camino",
    "✅ Entregados",
]
choice = st.selectbox(
    "Sección:", menu, label_visibility="collapsed"
)


# ---------------------------------------------------------
# 1. REGISTRAR ORDEN
# ---------------------------------------------------------
if choice == "➕ Registrar":
  st.subheader("Registrar Nueva Orden")

  with st.form("form_registro", clear_on_submit=True):
    tracking = st.text_input("Número de Tracking *")
    descripcion = st.text_input(
        "Descripción *", placeholder="Ej: Ropa, accesorios..."
    )
    monto = st.text_input("Monto ($)", placeholder="Ej: 9 o 15.50")

    enviar = st.form_submit_button("Guardar Orden")

    if enviar:
      if not tracking or not descripcion:
        st.warning("Completa el Tracking y la Descripción.")
      else:
        nueva_fila = pd.DataFrame({
            "tracking": [tracking.strip()],
            "descripcion": [descripcion.strip()],
            "monto": [monto.strip()],
            "fecha": [datetime.now().strftime("%d/%m/%Y")],
            "estado": ["Espera"],
        })

        df = pd.concat([df, nueva_fila], ignore_index=True)
        guardar_datos(df)
        st.success("¡Guardado con éxito!")


# ---------------------------------------------------------
# FUNCION PARA MOSTRAR TARJETAS COMPACTAS
# ---------------------------------------------------------
def mostrar_paquetes(estado_filtro):
  busqueda = st.text_input(
      "🔍 Buscar tracking...", key=f"search_{estado_filtro}"
  )

  filtrados = df[df["estado"] == estado_filtro]
  if busqueda:
    filtrados = filtrados[
        filtrados["tracking"].str.contains(busqueda, case=False, na=False)
    ]

  st.caption(f"Total: {len(filtrados)}")

  if filtrados.empty:
    st.info("No hay paquetes aquí.")
    return

  for index, row in filtrados.iterrows():
    # Contenedor con diseño de tarjeta elegante y sin líneas feas
    with st.container():
      st.markdown(
          f"""
            <div style="background-color: #1e1e1e; padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #333;">
                <span style="font-size: 14px; color: #bbb;"><b>Trk:</b> {row['tracking']}</span> | 
                <span style="font-size: 14px; color: #fff;"><b>Desc:</b> {row['descripcion']}</span><br>
                <span style="font-size: 13px; color: #2ecc71;"><b>Monto:</b> ${row['monto']}</span> 
                <span style="font-size: 12px; color: #888; float: right;">{row['fecha']}</span>
            </div>
            """,
          unsafe_allow_html=True,
      )

      # Botones pequeños distribuidos horizontalmente según el estado
      cols = st.columns(2)

      if estado_filtro == "Espera":
        with cols[0]:
          if st.button("🏢 Al Casillero", key=f"c1_{index}"):
            df.at[index, "estado"] = "Casillero"
            guardar_datos(df)
            st.rerun()
        with cols[1]:
          if st.button("🗑️ Borrar", key=f"del_{index}"):
            df = df.drop(index)
            guardar_datos(df)
            st.rerun()

      elif estado_filtro == "Casillero":
        with cols[0]:
          if st.button("↩️ Volver", key=f"c2_{index}"):
            df.at[index, "estado"] = "Espera"
            guardar_datos(df)
            st.rerun()
        with cols[1]:
          if st.button("🚢 En Camino", key=f"c3_{index}"):
            df.at[index, "estado"] = "Camino"
            guardar_datos(df)
            st.rerun()

      elif estado_filtro == "Camino":
        with cols[0]:
          if st.button("↩️ Volver", key=f"c4_{index}"):
            df.at[index, "estado"] = "Casillero"
            guardar_datos(df)
            st.rerun()
        with cols[1]:
          if st.button("✅ En Mis Manos", key=f"c5_{index}"):
            df.at[index, "estado"] = "Entregados"
            guardar_datos(df)
            st.rerun()

      elif estado_filtro == "Entregados":
        with cols[0]:
          if st.button("🗑️ Borrar", key=f"del2_{index}"):
            df = df.drop(index)
            guardar_datos(df)
            st.rerun()


# ---------------------------------------------------------
# 2. VISTAS DE ESTADOS
# ---------------------------------------------------------
if choice == "⏳ Espera":
  st.subheader("En Espera")
  mostrar_paquetes("Espera")

elif choice == "🏢 Casillero":
  st.subheader("En Casillero")
  mostrar_paquetes("Casillero")

elif choice == "🚢 Camino":
  st.subheader("En Camino")
  mostrar_paquetes("Camino")

elif choice == "✅ Entregados":
  st.subheader("En Mis Manos")
  mostrar_paquetes("Entregados")
