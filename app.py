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
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    if "gcp_service_account" in st.secrets:
        creds_info = st.secrets["gcp_service_account"]
        if isinstance(creds_info, str): creds_info = json.loads(creds_info)
        info = dict(creds_info)
        if "\\n" in info["private_key"]: info["private_key"] = info["private_key"].replace("\\n", "\n")
        creds = Credentials.from_service_account_info(info, scopes=scope)
    else:
        creds = Credentials.from_service_account_file("info-bot-mmwp-7183fe52f9b4.json", scopes=scope)
    return gspread.authorize(creds)

def log_to_sheets(data_list):
    if not data_list: return False
    try:
        client = get_gspread_client()
        sheet = client.open("Fut").worksheet("logger1")
        formatted_data = [[str(cell) for cell in row] for row in data_list]
        sheet.append_rows(formatted_data, value_input_option="USER_ENTERED")
        st.toast(f"✅ {len(data_list)} filas registradas", icon="📊")
        return True
    except Exception as e:
        st.error(f"❌ Error en Google Sheets: {e}")
        return False

# =========================
# CONFIGURACIÓN Y DATOS
# =========================
@dataclass
class Player:
    name: str
    features: Set[str]

FORMACIONES = {"2-3-1": [2, 3, 1], "2-2-2": [2, 2, 2], "3-2-1": [3, 2, 1]}

def inicializar_estado():
    st.session_state.players_data = {
        "Zorry": Player("Zorry", {"PO"}), "Alan": Player("Alan", {"PO","ML", "MC", "AT"}),
        "Kevin": Player("Kevin", {"ML", "MC", "DF"}), "Hieu": Player("Hieu", {"ML"}),
        "Nam": Player("Nam", {"ML", "DF"}), "Luis": Player("Luis", {"DF"}),
        "Quero": Player("Quero", {"PO","MC", "DF", "ML"}), "Loco": Player("Loco", {"PO","DF", "ML"}),
        "Jaír": Player("Jaír", {"ML", "DF"}), "JP": Player("JP", {"AT", "ML"}),
        "Báez": Player("Báez", {"ML", "MC"}), "Mario": Player("Mario", {"MC", "DF"}),
        "Fer": Player("Fer", {"AT"}), "Portero invitado": Player("Portero invitado", {"PO"}),
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

if 'players_data' not in st.session_state: inicializar_estado()

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
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

def get_status_emoji(player_name):
    entry_ts = st.session_state.entry_timestamp.get(player_name)
    if entry_ts is None: return "🟢"
    tiempo_turno = (time.time() - entry_ts) / 60
    if tiempo_turno >= 2: return "🔴"
    if tiempo_turno >= 1: return "🟡"
    return "🟢"

def execute_swap(player_in, player_out):
    now = time.time()
    st.session_state.accumulated_time[player_out] += (now - st.session_state.entry_timestamp[player_out])
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
    for b in get_bench():
        st.write(f"{get_status_emoji(b)} **{b}** (Últ: {st.session_state.last_position[b]})")
    
    if st.session_state.expulsados:
        st.divider()
        st.header("🟥 Expulsados")
        for ex in st.session_state.expulsados: st.write(f"- ~~{ex}~~")

st.subheader("📐 Configuración Táctica")
formacion_actual = st.selectbox("Formación:", options=list(FORMACIONES.keys()), 
                         index=list(FORMACIONES.keys()).index(st.session_state.formacion_elegida),
                         disabled=st.session_state.match_running)

if formacion_actual != st.session_state.formacion_elegida:
    st.session_state.formacion_elegida = formacion_actual
    st.session_state.lineup = {"C0_PO": [], "C1_DEF": [], "C2_MID": [], "C3_ATK": []}
    st.rerun()

f_nums = FORMACIONES[st.session_state.formacion_elegida]
CONFIG_UI = {"C0_PO": {"label": "Portero", "size": 1, "req": "PO"}, "C1_DEF": {"label": "Defensa", "size": f_nums[0], "req": "DF"},
             "C2_MID": {"label": "Mediocampo", "size": f_nums[1], "req": "ML"}, "C3_ATK": {"label": "Ataque", "size": f_nums[2], "req": "AT"}}

cols_aln = st.columns(4)
for i, (cid, cfg) in enumerate(CONFIG_UI.items()):
    with cols_aln[i]:
        others = [p for k, v in st.session_state.lineup.items() if k != cid for p in v]
        opts = [n for n, p in st.session_state.players_data.items() if cfg["req"] in p.features and n not in others and n not in st.session_state.expulsados]
        selected = st.multiselect(f"{cfg['label']} ({cfg['size']})", opts, default=st.session_state.lineup[cid], max_selections=cfg["size"], key=f"ui_{cid}", disabled=st.session_state.match_running)
        if not st.session_state.match_running: st.session_state.lineup[cid] = selected

st.divider()
if not st.session_state.match_running:
    total_actual = sum(len(v) for v in st.session_state.lineup.values())
    if st.button("🚀 INICIAR PARTIDO", type="primary", width='stretch', disabled=(total_actual < (sum(f_nums) + 1))):
        st.session_state.match_running, st.session_state.start_match_time = True, time.time()
        update_last_positions()
        now = time.time()
        for p_list in st.session_state.lineup.values():
            for p in p_list: st.session_state.entry_timestamp[p] = now
        st.rerun()
else:
    c1, c2, c3, c4 = st.columns([1.5, 1.5, 2, 1])
    fmt_txt = f"'{st.session_state.formacion_elegida}"
    with c1: p_in = st.selectbox("Entra:", ["-"] + get_bench())
    with c2:
        on_field_list = [p for plist in st.session_state.lineup.values() for p in plist]
        p_out = st.selectbox("Sale:", ["-"] + on_field_list)
    with c3:
        p_exp_select = st.selectbox("🟥 Expulsar:", ["-"] + [n for n in st.session_state.players_data if n not in st.session_state.expulsados])
        if p_exp_select != "-":
            now = time.time()
            if st.session_state.entry_timestamp[p_exp_select]:
                st.session_state.accumulated_time[p_exp_select] += now - st.session_state.entry_timestamp[p_exp_select]
            st.session_state.expulsados.append(p_exp_select)
            st.session_state.entry_timestamp[p_exp_select] = None
            for cid in st.session_state.lineup:
                if p_exp_select in st.session_state.lineup[cid]: st.session_state.lineup[cid].remove(p_exp_select)
            log_to_sheets([[datetime.now().strftime("%Y-%m-%d %H:%M:%S"), p_exp_select, st.session_state.last_position[p_exp_select], fmt_txt, round(st.session_state.accumulated_time[p_exp_select]/60, 2), 1]])
            st.rerun()
    with c4:
        st.write(" ")
        st.write(" ")
        if p_in != "-" and p_out != "-" and st.button("✅ Swap", type="primary", width='stretch'):
            execute_swap(p_in, p_out)
            st.rerun()

if st.session_state.match_running:
    if st.button("🛑 FINALIZAR PARTIDO", type="secondary", width='stretch'):
        now = time.time()
        log_batch, ts = [], datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fmt_txt = f"'{st.session_state.formacion_elegida}"
        for p, acc in st.session_state.accumulated_time.items():
            total = acc + (now - st.session_state.entry_timestamp[p] if st.session_state.entry_timestamp[p] else 0)
            if total > 0:
                log_batch.append([ts, p, st.session_state.last_position[p], fmt_txt, round(total/60, 2), 1 if p in st.session_state.expulsados else 0])
        if log_batch: log_to_sheets(log_batch)
        inicializar_estado()
        st.rerun()
    elapsed = time.time() - st.session_state.start_match_time
    st.markdown(f"<h2 style='text-align: center; color: #ff4b4b;'>⏱️ {format_time(elapsed)}</h2>", unsafe_allow_html=True)

st.divider()
if any(t > 0 for t in st.session_state.accumulated_time.values()) or st.session_state.match_running:
    data, now = [], time.time()
    for p in st.session_state.players_data:
        if p in st.session_state.expulsados: continue
        acc, entry_ts = st.session_state.accumulated_time[p], st.session_state.entry_timestamp[p]
        if acc > 0 or entry_ts:
            total_segundos = acc + (now - entry_ts if entry_ts else 0)
            data.append({"Jugador": p, "Posición": st.session_state.last_position[p], "Minutos Totales": format_time(total_segundos), "Estado Turno": f"{'🏃' if entry_ts else '🪑'} {get_status_emoji(p)}"})
    # CORRECCIÓN FINAL: width='stretch' reemplaza a None para evitar StreamlitInvalidWidthError
    st.dataframe(data, width='stretch') 

if st.session_state.match_running:
    time.sleep(1)
    st.rerun()