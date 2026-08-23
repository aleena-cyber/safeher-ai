import streamlit as st
from pathlib import Path
from datetime import datetime
import json, uuid, re

# Optional components
try:
    from streamlit_geolocation import streamlit_geolocation
    GEO_AVAILABLE = True
except Exception:
    GEO_AVAILABLE = False

try:
    from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
    VIDEO_AVAILABLE = True
except Exception:
    VIDEO_AVAILABLE = False

st.set_page_config(page_title="SafeHer AI", page_icon="🌸", layout="wide")

BASE_DIR = Path("safeher_evidence")
BASE_DIR.mkdir(exist_ok=True)

# ---------- LIGHT/PINK THEME ----------
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"],
[data-testid="stAppViewBlockContainer"], .main, .block-container {
    background:#fff7fc !important;
    color:#333 !important;
}
h1,h2,h3,h4,h5,h6,p,label,li,small,span { color:#333 !important; }

.safeher-hero {
    background:linear-gradient(135deg,#ff5a9f,#d15cff) !important;
    border-radius:24px; padding:28px; margin-bottom:22px;
    text-align:center; box-shadow:0 8px 25px rgba(180,80,160,.15);
}
.safeher-hero h1,.safeher-hero p { color:#fff !important; }
.safeher-hero h1 { font-size:40px !important; margin:0 !important; }
.safeher-hero p { font-size:17px !important; margin:8px 0 0 !important; }

.card,.incident-box,.evidence-box {
    background:#fff !important; color:#333 !important;
    border-radius:16px; padding:16px; margin:12px 0;
    border:1px solid #ead1df; box-shadow:0 4px 15px rgba(120,60,120,.07);
}
.incident-box { background:#fff0f6 !important; border:2px solid #ff9bc4 !important; }
.evidence-box { border-left:6px solid #ff69a6; }
.evidence-box b { color:#b52f78 !important; }

.stButton > button, .stDownloadButton > button {
    background:#fff !important; color:#333 !important;
    border:2px solid #dfb8ce !important; border-radius:12px !important;
    font-weight:700 !important; min-height:44px !important;
}
.stButton > button p,.stButton > button span,
.stDownloadButton > button p,.stDownloadButton > button span {
    color:#333 !important;
}
.stButton > button:hover,.stDownloadButton > button:hover {
    background:#fff0f7 !important; border-color:#ff65a5 !important;
}
.stButton > button[kind="primary"] {
    background:linear-gradient(135deg,#ff4f91,#d35cff) !important;
    color:#fff !important; border:0 !important;
}
.stButton > button[kind="primary"] p,.stButton > button[kind="primary"] span {
    color:#fff !important;
}

[data-testid="stTextArea"] textarea,[data-testid="stTextInput"] input {
    background:#fff !important; color:#222 !important;
    -webkit-text-fill-color:#222 !important;
    border:2px solid #dfbfd2 !important; border-radius:12px !important;
}
[data-testid="stTextArea"] textarea::placeholder {
    color:#777 !important; -webkit-text-fill-color:#777 !important;
}
[data-testid="stCameraInput"] {
    background:#fff !important; border:1px solid #ead1df !important;
    border-radius:14px !important; padding:6px !important;
}
[data-testid="stCameraInput"] label,[data-testid="stCameraInput"] p {
    color:#333 !important;
}
[data-testid="stAlert"] p,[data-testid="stAlert"] span { color:#333 !important; }
[data-testid="stMetric"] {
    background:#fff !important; border:1px solid #ead1df !important;
    border-radius:12px !important;
}
[data-testid="stMetricLabel"] { color:#666 !important; }
[data-testid="stMetricValue"] { color:#333 !important; }
[data-testid="stExpander"] {
    background:#fff !important; border:1px solid #ead1df !important;
    border-radius:12px !important;
}
hr { border-color:#ead1df !important; }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
defaults = {
    "incident_active": False,
    "incident_id": None,
    "incident_started": None,
    "sos_message": "",
    "evidence": [],
    "location_requested": False,
    "ai_result": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_name(v):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(v))

def incident_folder():
    if not st.session_state.incident_id:
        return BASE_DIR
    p = BASE_DIR / safe_name(st.session_state.incident_id)
    p.mkdir(parents=True, exist_ok=True)
    return p

def save_manifest():
    if not st.session_state.incident_id:
        return
    data = {
        "incident_id": st.session_state.incident_id,
        "incident_started": st.session_state.incident_started,
        "updated": now(),
        "evidence": st.session_state.evidence,
    }
    (incident_folder() / "evidence_manifest.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )

def add_evidence(kind, path, description):
    item = {
        "type": kind,
        "timestamp": now(),
        "incident_id": st.session_state.incident_id,
        "description": description,
        "file": str(path),
    }
    if not any(x["type"] == kind and x["file"] == str(path)
               for x in st.session_state.evidence):
        st.session_state.evidence.append(item)
        save_manifest()

def start_incident():
    st.session_state.incident_id = (
        "SH-" + datetime.now().strftime("%Y%m%d-%H%M%S") +
        "-" + uuid.uuid4().hex[:6].upper()
    )
    st.session_state.incident_started = now()
    st.session_state.incident_active = True
    st.session_state.sos_message = "SOS ACTIVATED — evidence collection is active."
    st.session_state.evidence = []
    st.session_state.location_requested = False
    st.session_state.ai_result = None
    incident_folder()
    save_manifest()

def classify(text):
    text = text.lower()
    high = ["attack","attacking","weapon","knife","gun","kidnap","kidnapping",
            "assault","threat","threatening","help me","danger","dangerous",
            "following me"]
    medium = ["stalking","stalker","unsafe","scared","suspicious","harassment",
              "harassing","stranger","uncomfortable","following"]
    if any(x in text for x in high):
        return "HIGH RISK", "The description contains indicators of a potentially immediate safety threat."
    if any(x in text for x in medium):
        return "MEDIUM RISK", "The description suggests a potentially unsafe situation."
    return "LOW RISK", "No strong high-risk indicators were detected."

# ---------- RESPONDER ----------
if st.query_params.get("mode") == "responder":
    st.markdown("""
    <div class="safeher-hero"><h1>🌸 SafeHer AI</h1>
    <p>Authorized Responder Dashboard</p></div>
    """, unsafe_allow_html=True)

    if st.query_params.get("key") != "safeher-demo":
        st.error("🔐 Unauthorized responder access.")
        if st.button("⬅️ Back to SafeHer AI", key="responder_bad_back"):
            st.query_params.clear()
            st.rerun()
        st.stop()

    st.success("✅ Authorized responder access granted.")
    st.header("🚨 Emergency Incidents")

    incidents = sorted([p for p in BASE_DIR.iterdir() if p.is_dir()],
                       key=lambda p: p.name, reverse=True)

    if not incidents:
        st.info("No incident evidence has been recorded yet.")

    for incident in incidents:
        mf = incident / "evidence_manifest.json"
        if not mf.exists():
            continue
        try:
            manifest = json.loads(mf.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
        iid = manifest.get("incident_id", incident.name)

        with st.expander(f"🚨 {iid}"):
            st.write("🕒 Started:", manifest.get("incident_started", "Unknown"))
            evidence = manifest.get("evidence", [])
            if not evidence:
                st.info("No evidence captured.")
            for item in evidence:
                st.markdown(f"""
                <div class="evidence-box">
                <b>📌 {item.get("type","")}</b><br>
                🕒 {item.get("timestamp","")}<br>
                🆔 {item.get("incident_id","")}<br>
                📝 {item.get("description","")}<br>
                📁 {item.get("file","")}
                </div>
                """, unsafe_allow_html=True)

    if st.button("⬅️ Back to SafeHer AI", key="responder_good_back"):
        st.query_params.clear()
        st.rerun()
    st.stop()

# ---------- MAIN ----------
st.markdown("""
<div class="safeher-hero">
<h1>🌸 SafeHer AI</h1>
<p>AI-assisted personal safety, emergency evidence capture and responder support</p>
</div>
""", unsafe_allow_html=True)

if st.session_state.incident_active:
    st.markdown(f"""
    <div class="incident-box">
    🚨 <b>INCIDENT ACTIVE</b><br>
    🆔 {st.session_state.incident_id}<br>
    🕒 {st.session_state.incident_started}
    </div>
    """, unsafe_allow_html=True)
else:
    st.success("🟢 SafeHer is ready. Press SOS if you feel unsafe.")

st.markdown("""
<div class="card">
<h2>🚨 Emergency SOS</h2>
<p>Creates a unique incident and enables evidence capture.</p>
</div>
""", unsafe_allow_html=True)

if st.button("🚨 ACTIVATE SOS", type="primary",
             use_container_width=True, key="sos_button"):
    if not st.session_state.incident_active:
        start_incident()
        st.rerun()
    else:
        st.warning("An incident is already active.")

if st.session_state.sos_message:
    st.warning(st.session_state.sos_message)

# ---------- EVIDENCE ----------
st.header("📸 Emergency Evidence Capture")

if not st.session_state.incident_active:
    st.info("Activate SOS first.")
else:
    p = incident_folder()

    # Snapshot: deliberately narrow like the earlier version
    st.subheader("📷 Emergency Snapshot")
    st.caption("Capture an emergency snapshot.")
    _, cam, _ = st.columns([1, 2, 1])
    with cam:
        snap = st.camera_input("Take emergency snapshot", key="safeher_snapshot")

    if snap is not None:
        f = p / f'{st.session_state.incident_id}_snapshot_{datetime.now():%Y%m%d_%H%M%S}.jpg'
        if not f.exists():
            f.write_bytes(snap.getvalue())
            add_evidence("SNAPSHOT", f, "Camera snapshot captured during active incident.")
        st.success("✅ Snapshot saved successfully.")

    # Location
    st.divider()
    st.subheader("📍 Emergency Location")
    st.caption("Capture your current GPS location.")

    if st.button("📍 CAPTURE MY LOCATION", use_container_width=True,
                 key="safeher_location_button"):
        st.session_state.location_requested = True
        st.rerun()

    if st.session_state.location_requested:
        if GEO_AVAILABLE:
            # IMPORTANT: no key argument. Compatible with streamlit-geolocation versions.
            location = streamlit_geolocation()
            if location and location.get("latitude") is not None and location.get("longitude") is not None:
                lat, lon = location["latitude"], location["longitude"]
                acc = location.get("accuracy")
                data = {
                    "incident_id": st.session_state.incident_id,
                    "timestamp": now(),
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": acc,
                }
                lf = p / f"{st.session_state.incident_id}_location.json"
                lf.write_text(json.dumps(data, indent=2), encoding="utf-8")
                add_evidence("LOCATION", lf, f"GPS: {lat}, {lon}")
                st.success("✅ Location captured successfully.")
                c1, c2 = st.columns(2)
                c1.metric("📍 Latitude", str(lat))
                c2.metric("📍 Longitude", str(lon))
                if acc is not None:
                    st.caption(f"🎯 Accuracy: {acc} meters")
                try:
                    st.map({"latitude": [lat], "longitude": [lon]})
                except Exception:
                    pass
            else:
                st.info("📍 Allow location access in your browser, then press 📍 CAPTURE MY LOCATION again.")
        else:
            st.error("📍 Location component unavailable. Check requirements.txt.")

    # Video
    st.divider()
    st.subheader("🎥 Emergency Video Capture")
    st.caption("Press START below to activate the emergency camera.")

    if VIDEO_AVAILABLE:
        rtc = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
        video = webrtc_streamer(
            key=f"safeher_video_{st.session_state.incident_id}",
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
            media_toggle_controls=True,
        )
        if video.state.playing:
            st.success("🔴 Emergency camera is ACTIVE.")
        else:
            st.info("⏸️ Camera is waiting. Press START in the camera box.")
        st.caption("Camera only — microphone is disabled.")
    else:
        st.error("🎥 Video component unavailable. Check streamlit-webrtc and av.")

# ---------- EVIDENCE LIST ----------
st.divider()
st.header("🛡️ Evidence Captured")

if not st.session_state.evidence:
    st.info("No completed evidence actions yet.")
else:
    for n, item in enumerate(reversed(st.session_state.evidence), 1):
        st.markdown(f"""
        <div class="evidence-box">
        <b>#{n} {item["type"]}</b><br>
        🕒 {item["timestamp"]}<br>
        🆔 {item["incident_id"]}<br>
        📝 {item["description"]}<br>
        📁 {item["file"]}
        </div>
        """, unsafe_allow_html=True)

# ---------- AI ----------
st.header("🤖 AI Safety Classification")
description = st.text_area(
    "Describe the situation",
    placeholder="Example: Someone has been following me for the last 10 minutes...",
    key="safeher_ai_description",
)

if st.button("🤖 Analyze Safety Situation", key="safeher_ai_button"):
    if description.strip():
        st.session_state.ai_result = classify(description)
    else:
        st.warning("Please describe the situation first.")

if st.session_state.ai_result:
    risk, explanation = st.session_state.ai_result
    if risk == "HIGH RISK":
        st.error(f"🚨 {risk}: {explanation}")
    elif risk == "MEDIUM RISK":
        st.warning(f"⚠️ {risk}: {explanation}")
    else:
        st.success(f"🟢 {risk}: {explanation}")

# ---------- INCIDENT CONTROLS ----------
st.header("⚙️ Incident Controls")

if st.session_state.incident_active:
    if st.button("🛑 End Incident", key="safeher_end_incident"):
        st.session_state.incident_active = False
        st.session_state.sos_message = "Incident ended. Evidence remains saved."
        save_manifest()
        st.rerun()

if st.session_state.incident_id:
    mf = incident_folder() / "evidence_manifest.json"
    if mf.exists():
        st.download_button(
            "⬇️ Download Incident Manifest",
            mf.read_bytes(),
            file_name=f"{st.session_state.incident_id}_manifest.json",
            mime="application/json",
            key="safeher_download_manifest",
        )

# ---------- RESPONDER ACCESS ----------
st.divider()
st.header("🛡️ Responder Access")
st.info("Authorized responders can open the SafeHer emergency evidence dashboard.")

if st.button("🛡️ Open Responder Dashboard",
             use_container_width=True, key="safeher_responder_button"):
    st.query_params["mode"] = "responder"
    st.query_params["key"] = "safeher-demo"
    st.rerun()

st.divider()
st.caption("🌸 SafeHer AI — Personal safety technology demonstration.")
