import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

st.set_page_config(
    page_title="Mi Casillero Personal",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Limpiar cualquier caché vieja de Streamlit para obligarlo a leer el código nuevo
st.cache_data.clear()

st.markdown("""
<style>
    .main { background-color: #f7f9fc; }
    .stButton>button { border-radius: 4px; font-weight: 500; font-size: 12px; padding: 2px 8px; }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "mis_paquetes_simple.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            df = pd.read_csv(CSV_FILE, dtype=str)
            df = df.fillna("")
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
            return df
        except:
            return pd.DataFrame(columns=[
                "id", "tracking", "descripcion", "monto", "estado", 
                "fecha_registro", "foto_compra", "foto_casillero"
            ])
    else:
        return pd.DataFrame(columns=[
            "id", "tracking", "descripcion", "monto", "estado", 
            "fecha_registro", "foto_compra", "foto_casillero"
        ])

def save_and_update(df):
    for col in df.columns:
        df[col] = df[col].astype(str).str.strip()
    df.to_csv(CSV_FILE, index=False)
    st.session_state["df_packages"] = df

# Forzar recarga fresca del estado
st.session_state["df_packages"] = load_data()

st.markdown("### 📦 MI CONTROL DE PAQUETES")

tab_registrar, tab_espera, tab_casillero, tab_camino = st.tabs([
    "➕ Registrar Orden", 
    "⏳ En Espera", 
    "🏢 En Casillero", 
    "🚢 En Camino"
])

with tab_registrar:
    st.markdown("#### ➕ Registrar Nueva Orden (1688)")
    with st.form("form_nueva_orden", clear_on_submit=True):
        tracking_val = st.text_input("Número de Tracking / Guía de 1688 *").strip()
        desc_val = st.text_area("Descripción de lo que viene *", placeholder="Ej: Ropa deportiva, accesorios, etc.")
        monto_val = st.text_input("Monto Pagado ($)", placeholder="Ej: 9 o 15.50").strip()
        
        st.markdown("**📸 Foto de Compra (Captura de 1688):**")
        foto_compra_sub = st.file_uploader("Sube la captura de tu compra:", type=["jpg", "png", "jpeg"], key="f_compra_ini")
        
        btn_guardar = st.form_submit_button("Crear Orden en Espera")
        if btn_guardar:
            if not tracking_val or not desc_val:
                st.error("Por favor completa el tracking y la descripción.")
            else:
                nuevo_id = datetime.now().strftime("%Y%m%d%H%M%S")
                fecha_hoy = datetime.now().strftime("%d/%m/%Y")
                
                path_compra = ""
                if foto_compra_sub is not None:
                    img_dir = "fotos_casillero"
                    os.makedirs(img_dir, exist_ok=True)
                    path_compra = os.path.join(img_dir, f"compra_{tracking_val}_{nuevo_id}.jpg")
                    Image.open(foto_compra_sub).save(path_compra)
                
                nuevo_item = {
                    "id": str(nuevo_id),
                    "tracking": str(tracking_val),
                    "descripcion": str(desc_val),
                    "monto": str(monto_val) if monto_val else "0",
                    "estado": "En espera",
                    "fecha_registro": fecha_hoy,
                    "foto_compra": str(path_compra),
                    "foto_casillero": ""
                }
                
                df_actual = load_data()
                df_actual = pd.concat([df_actual, pd.DataFrame([nuevo_item])], ignore_index=True)
                save_and_update(df_actual)
                st.success("¡Orden creada con éxito!")
                st.rerun()

with tab_espera:
    st.markdown("#### Paquetes en Tránsito (Esperando que lleguen al casillero en China)")
    
    df_full = st.session_state["df_packages"]
    df_esp = df_full[df_full["estado"] == "En espera"].copy() if len(df_full) > 0 else pd.DataFrame()
    
    busqueda_rapida = st.text_input(
        "🔍 Buscar tracking en espera:", 
        value="", 
        placeholder="Escribe el número de tracking...", 
        key="txt_busqueda_esp",
        label_visibility="collapsed"
    ).strip()

    # FILTRO 100% EXCLUSIVO: Solo evalúa la columna 'tracking', ignorando montos y fechas por completo
    if len(df_esp) > 0 and busqueda_rapida != "":
        df_esp = df_esp[df_esp["tracking"].astype(str).str.startswith(busqueda_rapida)].reset_index(drop=True)
    elif len(df_esp) > 0:
        df_esp = df_esp.reset_index(drop=True)

    st.markdown(f"**Resultados encontrados: {len(df_esp)}**")
    
    if len(df_esp) == 0:
        st.info("No hay paquetes pendientes que coincidan con ese número de seguimiento.")
    else:
        for idx, row in df_esp.iterrows():
            p_id = str(row['id'])
            
            with st.container(border=True):
                col_info, col_fotos = st.columns([1.3, 1])
                
                with col_info:
                    st.markdown(f"**📌 Seguimiento:** {row['tracking']}")
                    st.markdown(f"**📝 Descripción:** {row['descripcion']}")
                    st.markdown(f"**💰 Monto:** ${row['monto']} | **📅:** {row['fecha_registro']}")
                    
                    st.markdown("---")
                    
                    b1, b2, b3, b4 = st.columns(4)
                    with b1:
                        if st.button("🛒", key=f"fcomp_{p_id}"):
                            st.session_state[f"edit_comp_{p_id}"] = not st.session_state.get(f"edit_comp_{p_id}", False)
                    with b2:
                        if st.button("📦 ", key=f"fcas_{p_id}"):
                            st.session_state[f"edit_cas_{p_id}"] = not st.session_state.get(f"edit_cas_{p_id}", False)
                    with b3:
                        if st.button("🏢 Al casillero", key=f"rec_{p_id}"):
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id, "estado"] = "En casillero"
                            save_and_update(df_mod)
                            st.rerun()
                    with b4:
                        if st.button("🗑️", key=f"del_esp_{p_id}"):
                            df_mod = load_data()
                            df_mod = df_mod[df_mod["id"] != p_id]
                            save_and_update(df_mod)
                            st.rerun()
                
                with col_fotos:
                    fc1, fc2 = st.columns(2)
                    with fc1:
                        st.caption("🛒 Compra")
                        if row['foto_compra'] != "" and os.path.exists(str(row['foto_compra'])):
                            st.image(str(row['foto_compra']), width=80)
                        else:
                            st.caption("Sin foto")
                    with fc2:
                        st.caption("📦 Casillero")
                        if row['foto_casillero'] != "" and os.path.exists(str(row['foto_casillero'])):
                            st.image(str(row['foto_casillero']), width=80)
                        else:
                            st.caption("Pendiente")
                
                if st.session_state.get(f"edit_comp_{p_id}", False):
                    st.markdown("---")
                    nueva_compra = st.file_uploader(f"Actualizar foto de compra para {row['tracking']}:", type=["jpg", "png", "jpeg"], key=f"up_comp_{p_id}")
                    if nueva_compra is not None:
                        if st.button("💾 Guardar foto compra", key=f"btn_save_comp_{p_id}"):
                            img_dir = "fotos_casillero"
                            os.makedirs(img_dir, exist_ok=True)
                            path_comp = os.path.join(img_dir, f"compra_{row['tracking']}_{p_id}.jpg")
                            Image.open(nueva_compra).save(path_comp)
                            
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id, "foto_compra"] = str(path_comp)
                            save_and_update(df_mod)
                            st.session_state[f"edit_comp_{p_id}"] = False
                            st.rerun()

                if st.session_state.get(f"edit_cas_{p_id}", False):
                    st.markdown("---")
                    nueva_cas = st.file_uploader(f"Actualizar foto de casillero para {row['tracking']}:", type=["jpg", "png", "jpeg"], key=f"up_cas_{p_id}")
                    if nueva_cas is not None:
                        if st.button("💾 Guardar foto casillero", key=f"btn_save_cas_{p_id}"):
                            img_dir = "fotos_casillero"
                            os.makedirs(img_dir, exist_ok=True)
                            path_cas = os.path.join(img_dir, f"casillero_{row['tracking']}_{p_id}.jpg")
                            Image.open(nueva_cas).save(path_cas)
                            
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id, "foto_casillero"] = str(path_cas)
                            save_and_update(df_mod)
                            st.session_state[f"edit_cas_{p_id}"] = False
                            st.rerun()

with tab_casillero:
    st.markdown("#### Paquetes en el Casillero")
    df_full_cas = st.session_state["df_packages"]
    df_cas = df_full_cas[df_full_cas["estado"] == "En casillero"].copy() if len(df_full_cas) > 0 else pd.DataFrame()
    
    busq_cas = st.text_input(
        "🔍 Buscar en casillero:", 
        value="", 
        placeholder="Escribe el tracking...", 
        key="txt_busq_cas",
        label_visibility="collapsed"
    ).strip()
    
    if len(df_cas) > 0 and busq_cas != "":
        df_cas = df_cas[df_cas["tracking"].astype(str).str.startswith(busq_cas)].reset_index(drop=True)
    elif len(df_cas) > 0:
        df_cas = df_cas.reset_index(drop=True)
        
    st.markdown(f"**Total en casillero: {len(df_cas)}**")
    
    if len(df_cas) == 0:
        st.info("No hay paquetes en el casillero actualmente.")
    else:
        for idx, row in df_cas.iterrows():
            p_id_cas = str(row['id'])
            with st.container(border=True):
                col_info_c, col_fotos_c = st.columns([1.3, 1])
                
                with col_info_c:
                    st.markdown(f"**📌 Seguimiento:** {row['tracking']}")
                    st.markdown(f"**📝 Descripción:** {row['descripcion']}")
                    st.markdown(f"**💰 Monto:** ${row['monto']} | **📅:** {row['fecha_registro']}")
                    
                    st.markdown("---")
                    
                    c1, c2, c3 = st.columns(3)
                    
                    with c2:
                        if st.button("🔄 Devolver", key=f"reg_esp_{p_id_cas}"):
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id_cas, "estado"] = "En espera"
                            save_and_update(df_mod)
                            st.rerun()
                    with c3:
                        if st.button("🚢 En Camino", key=f"to_camino_{p_id_cas}"):
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id_cas, "estado"] = "En camino"
                            save_and_update(df_mod)
                            st.rerun()
                
                with col_fotos_c:
                    fc_r1, fc_r2 = st.columns(2)
                    with fc_r1:
                        st.caption("🛒")
                        if row['foto_compra'] != "" and os.path.exists(str(row['foto_compra'])):
                            st.image(str(row['foto_compra']), width=80)
                    with fc_r2:
                        st.caption("📦")
                        if row['foto_casillero'] != "" and os.path.exists(str(row['foto_casillero'])):
                            st.image(str(row['foto_casillero']), width=80)

                if st.session_state.get(f"edit_cas_c_{p_id_cas}", False):
                    st.markdown("---")
                    nueva_cas_c = st.file_uploader(f"Actualizar foto de casillero para {row['tracking']}:", type=["jpg", "png", "jpeg"], key=f"up_cas_c_{p_id_cas}")
                    if nueva_cas_c is not None:
                        if st.button("💾 Guardar foto", key=f"btn_save_cas_c_{p_id_cas}"):
                            img_dir = "fotos_casillero"
                            os.makedirs(img_dir, exist_ok=True)
                            path_cas = os.path.join(img_dir, f"casillero_{row['tracking']}_{p_id_cas}.jpg")
                            Image.open(nueva_cas_c).save(path_cas)
                            
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id_cas, "foto_casillero"] = str(path_cas)
                            save_and_update(df_mod)
                            st.session_state[f"edit_cas_c_{p_id_cas}"] = False
                            st.rerun()

with tab_camino:
    st.markdown("#### Paquetes En Camino")
    df_full_cam = st.session_state["df_packages"]
    df_cam = df_full_cam[df_full_cam["estado"] == "En camino"].copy() if len(df_full_cam) > 0 else pd.DataFrame()
    
    busq_cam = st.text_input(
        "🔍 Buscar en camino:", 
        value="", 
        placeholder="Escribe el tracking...", 
        key="txt_busq_cam",
        label_visibility="collapsed"
    ).strip()
    
    if len(df_cam) > 0 and busq_cam != "":
        df_cam = df_cam[df_cam["tracking"].astype(str).str.startswith(busq_cam)].reset_index(drop=True)
    elif len(df_cam) > 0:
        df_cam = df_cam.reset_index(drop=True)
        
    st.markdown(f"**Total en camino: {len(df_cam)}**")
    
    if len(df_cam) == 0:
        st.info("No hay paquetes en camino actualmente.")
    else:
        for idx, row in df_cam.iterrows():
            p_id_cam = str(row['id'])
            with st.container(border=True):
                col_info_m, col_fotos_m = st.columns([1.3, 1])
                
                with col_info_m:
                    st.markdown(f"**📌 Seguimiento:** {row['tracking']}")
                    st.markdown(f"**📝 Descripción:** {row['descripcion']}")
                    st.markdown(f"**💰 Monto:** ${row['monto']} | **📅:** {row['fecha_registro']}")
                    
                    st.markdown("---")
                    
                    m1, m2 = st.columns(2)
                    with m1:
                        if st.button("🔄 Devolver", key=f"reg_cas_{p_id_cam}"):
                            df_mod = load_data()
                            df_mod.loc[df_mod["id"] == p_id_cam, "estado"] = "En casillero"
                            save_and_update(df_mod)
                            st.rerun()
                    with m2:
                        if st.button("✅ En Mis Manos", key=f"fin_{p_id_cam}"):
                            df_mod = load_data()
                            df_mod = df_mod[df_mod["id"] != p_id_cam]
                            save_and_update(df_mod)
                            st.rerun()
                
                with col_fotos_m:
                    fm_r1, fm_r2 = st.columns(2)
                    with fm_r1:
                        st.caption("🛒 Compra")
                        if row['foto_compra'] != "" and os.path.exists(str(row['foto_compra'])):
                            st.image(str(row['foto_compra']), width=80)
                    with fm_r2:
                        st.caption("📦 Casillero")
                        if row['foto_casillero'] != "" and os.path.exists(str(row['foto_casillero'])):
                            st.image(str(row['foto_casillero']), width=80)
