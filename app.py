import streamlit as st
import time
import gspread
from google.oauth2.service_account import Credentials
from dataclasses import dataclass
from typing import Set
from datetime import datetime
import json

# =========================
# CONFIGURACIÓN GOOGLE SHEETS
# =========================
@st.cache_resource(show_spinner=False)
def get_gspread_client():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        if isinstance(creds_info, str):
            creds_info = json.loads(creds_info)
        info = dict(creds_info)
        if "\\n" in info["private_key"]:
            info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(info, scopes=scope)
    else:
        creds = Credentials.from_service_account_file(
            "info-bot-mmwp-7183fe52f9b4.json",
            scopes=scope
        )
    return gspread.authorize(creds)

def log_to_sheets(data_list):
    if not data_list:
        return False

    status = st.empty()
    status.info("⏳ Registrando datos en Google Sheets...")

    try:
        client = get_gspread_client()
        sheet = client.open("Fut").worksheet("logger1")

        # El parámetro USER_ENTERED permite que Sheets interprete el "'" como formato de texto
        formatted_data = [[str(cell) for cell in row] for row in data_list]
        sheet.append_rows(
            formatted_data,
            value_input_option="USER_ENTERED"
        )

        status.empty()
        st.toast(f"✅ {len(data_list)} filas registradas", icon="📊")
        return True

    except Exception as e:
        status.empty()
        st.error(f"❌ Error en Google Sheets: {e}")
        return False

# =========================
# CONFIGURACIÓN Y DATOS
# =========================
@dataclass
class Player:
    name: str
    features: Set[str]

FORMACIONES = {
    "2-3-1": [2, 3, 1],
    "2-2-2": [2, 2, 2],
    "3-2-1": [3, 2, 1]
}

def inicializar_estado():
    st.session_state.players_data = {
        "Zorry": Player("Zorry", {"PO"}),
        "Alan": Player("Alan", {"PO","ML", "MC", "AT"}),
        "Kevin": Player("Kevin", {"ML", "MC", "DF"}),
        "Hieu": Player("Hieu", {"ML"}),
        "Nam": Player("Nam", {"ML", "DF"}),
        "Luis": Player("Luis", {"DF"}),
        "Quero": Player("Quero", {"PO","MC", "DF", "ML"}),
        "Loco": Player("Loco", {"PO","DF", "ML"}),
        "Jaír": Player("Jaír", {"ML", "DF"}),
        "JP": Player("JP", {"AT", "ML"}),
        "Báez": Player("Báez", {"ML", "MC"}),
        "Mario": Player("Mario", {"MC", "DF"}),
        "Fer": Player("Fer", {"AT"}),
        "Portero invitado": Player("Portero invitado", {"PO"}),
        "Jugador 1": Player("Jugador 1", {"ML", "MC", "AT", "DF"}),
        "Jugador 2": Player("Jugador 2", {"ML", "MC", "AT", "DF"}),
        "Jugador 3": Player("Jugador 3", {"ML", "MC", "AT", "DF"}),
    }
    st.session_state.accumulated_time = {n: 0.0 for n in st.session_state.players_data}
    st.session_state.entry_timestamp = {n: None for n in st.session_state.players_data}
    st.session_state.last_position = {n: "Banca" for n in st.session_state.players_data}
    st.session_state.match_running = False
    st.session_state.start_match_time = None 
    st.session_state.lineup = {"C0_PO": [], "C1_DEF": [], "C2_MID": [], "C3_ATK": []}
    st.session_state.expulsados = []
    st.session_state.formacion_elegida = "2-3-1"

if 'players_data' not in st.session_state:
    inicializar_estado()

# =========================
# LÓGICA AUXILIAR
# =========================
def update_last_positions():
    formation = st.session_state.formacion_elegida
    lineup = st.session_state.lineup
    for cid, players in lineup.items():
        for idx, p_name in enumerate(players):
            if cid == "C0_PO": pos = "PO"
            elif cid == "C1_DEF": pos = "DF"
            elif cid == "C3_ATK": pos = "AT"
            elif cid == "C2_MID":
                if formation == "2-3-1": pos = "MC" if idx == 1 else "ML"
                elif formation == "2-2-2": pos = "MC"
                else: pos = "ML"
            st.session_state.last_position[p_name] = pos

def format_time(seconds):
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def get_status_emoji(seconds):
    minutos = seconds / 60
    if minutos >= 2: return "🔴"
    if minutos >= 1: return "🟠"
    return "🟢"

def update_timers():
    now = time.time()
    for name in st.session_state.players_data:
        if st.session_state.entry_timestamp[name] is not None:
            st.session_state.accumulated_time[name] += now - st.session_state.entry_timestamp[name]
            st.session_state.entry_timestamp[name] = now

def execute_swap(player_in, player_out):
    update_timers()
    now = time.time()
    st.session_state.entry_timestamp[player_out] = None
    st.session_state.entry_timestamp[player_in] = now
    for cid, players in st.session_state.lineup.items():
        if player_out in players:
            st.session_state.lineup[cid] = [player_in if p == player_out else p for p in players]
            break
    update_last_positions()

def get_bench():
    on_field = [p for plist in st.session_state.lineup.values() for p in plist]
    return [p for p in st.session_state.players_data if p not in on_field and p not in st.session_state.expulsados]

# =========================
# INTERFAZ (UI)
# =========================
st.set_page_config(page_title="Tactical Tracker Pro", layout="wide")
st.title("⚽ RCB Tactical Time Tracker")

with st.sidebar:
    st.header("🪑 Banca")
    bench_list = get_bench()
    for b in bench_list:
        last_p = st.session_state.last_position[b]
        st.write(f"- **{b}** (Últ: {last_p})")
    
    if st.session_state.expulsados:
        st.divider()
        st.header("🟥 Expulsados")
        for ex in st.session_state.expulsados:
            st.write(f"- ~~{ex}~~")

# --- CONFIGURACIÓN TÁCTICA ---
st.subheader("📐 Configuración Táctica")
formacion_actual = st.selectbox("Formación:", options=list(FORMACIONES.keys()), 
                         index=list(FORMACIONES.keys()).index(st.session_state.formacion_elegida),
                         disabled=st.session_state.match_running)

if formacion_actual != st.session_state.formacion_elegida:
    st.session_state.formacion_elegida = formacion_actual
    st.session_state.lineup = {"C0_PO": [], "C1_DEF": [], "C2_MID": [], "C3_ATK": []}
    st.rerun()

f_nums = FORMACIONES[st.session_state.formacion_elegida]
CONFIG_UI = {
    "C0_PO":  {"label": "Portero", "size": 1, "req": "PO"},
    "C1_DEF": {"label": "Defensa", "size": f_nums[0], "req": "DF"},
    "C2_MID": {"label": "Mediocampo", "size": f_nums[1], "req": "ML"}, 
    "C3_ATK": {"label": "Ataque", "size": f_nums[2], "req": "AT"}
}

cols_aln = st.columns(4)
for i, (cid, cfg) in enumerate(CONFIG_UI.items()):
    with cols_aln[i]:
        others = [p for k, v in st.session_state.lineup.items() if k != cid for p in v]
        opts = [n for n, p in st.session_state.players_data.items() 
                if cfg["req"] in p.features and n not in others and n not in st.session_state.expulsados]
        
        selected = st.multiselect(f"{cfg['label']} ({cfg['size']})", opts, 
                                  default=st.session_state.lineup[cid], 
                                  max_selections=cfg["size"], key=f"ui_{cid}",
                                  disabled=st.session_state.match_running)
        if not st.session_state.match_running:
            st.session_state.lineup[cid] = selected

# --- GESTIÓN EN VIVO ---
st.divider()
st.subheader("🔄 Gestión en Vivo")

if not st.session_state.match_running:
    total_necesario = sum(f_nums) + 1
    total_actual = sum(len(v) for v in st.session_state.lineup.values())
    if st.button("🚀 INICIAR PARTIDO", type="primary", use_container_width=True, disabled=(total_actual < total_necesario)):
        st.session_state.match_running = True
        st.session_state.start_match_time = time.time()
        update_last_positions()
        now = time.time()
        for p_list in st.session_state.lineup.values():
            for p in p_list: st.session_state.entry_timestamp[p] = now
        st.rerun()
else:
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 1])
    # Forzamos texto en la formación para evitar error de fecha
    fmt_txt = f"'{st.session_state.formacion_elegida}"

    with c1:
        p_in = st.selectbox("Entra:", ["-"] + get_bench())
    with c2:
        if p_in != "-":
            feats_in = st.session_state.players_data[p_in].features
            targets = [p for cid, players in st.session_state.lineup.items() if CONFIG_UI[cid]["req"] in feats_in for p in players]
            p_out = st.selectbox("Sale:", ["-"] + targets)
        else:
            p_out = st.selectbox("Sale:", ["-"], disabled=True)
    with c3:
        posibles_expulsar = [n for n in st.session_state.players_data if n not in st.session_state.expulsados]
        exp = st.multiselect("🟥 Expulsar:", posibles_expulsar)
        if exp:
            update_timers()
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_batch = []
            for p_exp in exp:
                pos_label = st.session_state.last_position[p_exp]
                minutos = round(st.session_state.accumulated_time[p_exp]/60, 2)
                st.session_state.expulsados.append(p_exp)
                st.session_state.entry_timestamp[p_exp] = None
                for cid in st.session_state.lineup:
                    if p_exp in st.session_state.lineup[cid]: st.session_state.lineup[cid].remove(p_exp)
                log_batch.append([ts, p_exp, pos_label, fmt_txt, minutos, 1])
            
            ok = log_to_sheets(log_batch)
            if not ok: st.stop()
            st.rerun()
            
    with c4:
        st.write(" ")
        st.write(" ")
        if p_in != "-" and p_out != "-":
            if st.button("✅ Swap", type="primary", use_container_width=True):
                execute_swap(p_in, p_out)
                st.rerun()

if st.session_state.match_running:
    if st.button("🛑 FINALIZAR PARTIDO", type="secondary", use_container_width=True):
        update_timers()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_batch = []
        fmt_txt = f"'{st.session_state.formacion_elegida}"
        
        for p, t in st.session_state.accumulated_time.items():
            if t > 0:
                pos_label = st.session_state.last_position[p]
                minutos = round(t/60, 2)
                exp_val = 1 if p in st.session_state.expulsados else 0
                log_batch.append([ts, p, pos_label, fmt_txt, minutos, exp_val])
        
        if log_batch:
            ok = log_to_sheets(log_batch)
            if not ok:
                st.error("❌ No se pudo guardar el partido. NO se reinicia el estado.")
                st.stop()
            time.sleep(2) 
            
        inicializar_estado()
        st.rerun()
    
    elapsed = time.time() - st.session_state.start_match_time
    st.markdown(f"<h2 style='text-align: center; color: #ff4b4b;'>⏱️ {format_time(elapsed)}</h2>", unsafe_allow_html=True)

# --- TABLA TIEMPO REAL ---
st.divider()
if any(t > 0 for t in st.session_state.accumulated_time.values()) or st.session_state.match_running:
    update_timers()
    data = []
    for p in st.session_state.players_data:
        if p in st.session_state.expulsados: continue
        acc = st.session_state.accumulated_time[p]
        if acc > 0 or st.session_state.entry_timestamp[p]:
            pos = st.session_state.last_position[p]
            icono = "🏃" if st.session_state.entry_timestamp[p] else "🪑"
            semaforo = get_status_emoji(acc)
            data.append({
                "Jugador": p, 
                "Posición": pos, 
                "Minutos": format_time(acc),
                "Estado": f"{icono} {semaforo}"
            })
    
    st.dataframe(data, use_container_width=True)

if st.session_state.match_running:
    time.sleep(1)
    st.rerun()