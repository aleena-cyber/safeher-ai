import os, json, uuid
from pathlib import Path
from datetime import datetime
import streamlit as st

APP_DIR = Path(__file__).resolve().parent / "safeher_data"
EVIDENCE_DIR = APP_DIR / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

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

st.markdown("""
<style>

/* SAFEHER BACKGROUND */
.stApp {
    background: linear-gradient(135deg, #fff7fb, #f8f3ff, #eef7ff) !important;
}

.block-container {
    max-width: 1250px;
    padding-top: 25px;
}

/* TEXT */
h1, h2, h3, h4, h5, h6,
p, label, span {
    color: #222222 !important;
}

/* HERO */
.hero {
    padding: 30px;
    border-radius: 28px;
    background: linear-gradient(135deg, #ff5f9e, #a66cff);
    color: white !important;
    box-shadow: 0 12px 35px rgba(166,108,255,.25);
    margin-bottom: 22px;
}

.hero h1,
.hero p {
    color: white !important;
}

/* WHITE CARDS */
.card {
    background: #ffffff !important;
    border: 1px solid #eadcf0 !important;
    border-radius: 20px !important;
    padding: 20px !important;
    margin-bottom: 16px !important;
    color: #222222 !important;
}

/* INCIDENT */
.incident {
    background: #fff0f4 !important;
    border: 2px solid #ff8cad !important;
    border-radius: 18px !important;
    padding: 16px !important;
    margin-bottom: 18px !important;
    color: #222222 !important;
}

/* EVIDENCE */
.evidence {
    background: #ffffff !important;
    border-left: 5px solid #b16cff !important;
    border-radius: 14px !important;
    padding: 14px !important;
    margin-bottom: 12px !important;
    color: #222222 !important;
}

/* STREAMLIT EXPANDERS */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #eadcf0 !important;
    border-radius: 18px !important;
}

[data-testid="stExpander"] details {
    background: #ffffff !important;
}

[data-testid="stExpander"] summary {
    background: #ffffff !important;
    color: #333333 !important;
}

[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    color: #333333 !important;
}

/* BUTTONS */
.stButton > button {
    background: linear-gradient(135deg, #ff6fa5, #a66cff) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    font-weight: 700 !important;
    padding: 12px 20px !important;
}

.stButton > button p,
.stButton > button span {
    color: white !important;
}

/* TEXT AREA */
.stTextArea textarea {
    background: white !important;
    color: #222222 !important;
    border: 1px solid #e0cfe8 !important;
    border-radius: 12px !important;
}

.stTextArea textarea::placeholder {
    color: #777777 !important;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #555555 !important;
    padding: 30px;
}

</style>
""", unsafe_allow_html=True)

def now(): return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
def folder():
    if not st.session_state.get("incident_id"): return None
    p=EVIDENCE_DIR/st.session_state.incident_id; p.mkdir(parents=True,exist_ok=True); return p

def save_manifest():
    p=folder()
    if p: (p/"evidence_manifest.json").write_text(json.dumps(st.session_state.evidence,indent=2),encoding="utf-8")

def add_evidence(kind,path,description):
    st.session_state.evidence.append({"incident_id":st.session_state.incident_id,"type":kind,"file":str(path),"timestamp":now(),"description":description})
    save_manifest()

def start_incident():
    iid=f"SH-{datetime.now():%Y%m%d-%H%M%S}-{uuid.uuid4().hex[:6].upper()}"
    st.session_state.incident_id=iid; st.session_state.incident_active=True; st.session_state.incident_started=now(); st.session_state.evidence=[]
    p=folder(); (p/"incident_metadata.json").write_text(json.dumps({"incident_id":iid,"started":st.session_state.incident_started},indent=2),encoding="utf-8")

def classify(text):
    t=(text or "").lower(); high=["attack","follow","following","stalk","stalking","threat","danger","help","emergency","harass","kidnap","chase","abuse"]; med=["alone","suspicious","scared","unsafe","stranger"]
    if any(x in t for x in high): return "HIGH RISK","Immediate safety response is recommended."
    if any(x in t for x in med): return "MEDIUM RISK","Stay alert and consider activating SOS."
    return "LOW RISK","No strong emergency indicators detected."

for k,v in {"incident_active":False,"incident_id":None,"incident_started":None,"evidence":[],"ai_result":None,"sos_message":""}.items():
    st.session_state.setdefault(k,v)

# Responder mode
if st.query_params.get("mode","") == "responder":
    st.markdown(
        '<div class="hero"><h1>👮 SafeHer AI</h1>'
        '<p>Authorized Responder Dashboard</p></div>',
        unsafe_allow_html=True
    )

    key = st.text_input("Responder Key", type="password")

    if key != "safeher-demo":
        st.info("Enter the authorized responder key.")
        st.stop()

    incidents = sorted(
        [p for p in EVIDENCE_DIR.iterdir() if p.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if not incidents:
        st.info("No incidents recorded yet.")

        if st.button("⬅️ Back to SafeHer AI"):
            st.query_params.clear()
            st.rerun()

        st.stop()

    selected = st.selectbox(
        "Select Incident",
        incidents,
        format_func=lambda p: p.name
    )

    st.markdown(
        f'<div class="incident"><b>Incident ID:</b> {selected.name}</div>',
        unsafe_allow_html=True
    )

    mf = selected / "evidence_manifest.json"

    if mf.exists():
        for item in json.loads(mf.read_text(encoding="utf-8")):

            st.markdown(
                f'<div class="evidence">'
                f'<b>{item["type"]}</b><br>'
                f'🕒 {item["timestamp"]}<br>'
                f'📝 {item["description"]}'
                f'</div>',
                unsafe_allow_html=True
            )

            fp = Path(item["file"])

            if fp.exists():
                if fp.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
                    st.image(str(fp), use_container_width=True)
                else:
                    st.download_button(
                        "⬇️ Download " + fp.name,
                        fp.read_bytes(),
                        file_name=fp.name,
                        key="dl_" + uuid.uuid4().hex
                    )

    if st.button("⬅️ Back to SafeHer AI"):
        st.query_params.clear()
        st.rerun()

    st.stop()
st.markdown('<div class="hero"><h1>🌸 SafeHer AI</h1><p>AI-assisted personal safety, emergency evidence capture and responder support</p></div>',unsafe_allow_html=True)

if st.session_state.incident_active:
    st.markdown(f'<div class="incident">🚨 <b>INCIDENT ACTIVE</b><br>🆔 {st.session_state.incident_id}<br>🕒 {st.session_state.incident_started}</div>',unsafe_allow_html=True)
else: st.success("🟢 SafeHer is ready. Press SOS if you feel unsafe.")

st.markdown('<div class="card"><h2>🚨 Emergency SOS</h2><p>Creates a unique incident and enables evidence capture.</p></div>',unsafe_allow_html=True)
if st.button("🚨 ACTIVATE SOS",type="primary",use_container_width=True):
    if not st.session_state.incident_active: start_incident(); st.session_state.sos_message="SOS ACTIVATED — evidence collection is active."; st.rerun()
    else: st.warning("An incident is already active.")
if st.session_state.sos_message: st.warning(st.session_state.sos_message)

st.header("📸 Emergency Evidence Capture")
if not st.session_state.incident_active: st.info("Activate SOS first.")
else:
    p = folder()

    # =========================
    # SNAPSHOT
    # =========================
    st.subheader("📷 Emergency Snapshot")

    snap = st.camera_input(
        "Take emergency snapshot",
        key="camera"
    )

    if snap is not None:
        fp = p / f"{st.session_state.incident_id}_snapshot_{datetime.now():%Y%m%d_%H%M%S}.jpg"

        fp.write_bytes(snap.getvalue())

        add_evidence(
            "SNAPSHOT",
            fp,
            "Camera snapshot captured during active incident."
        )

        st.success("✅ Snapshot saved successfully.")

    # =========================
    # LOCATION
    # =========================
    st.divider()

    st.subheader("📍 Emergency Location")

    if "location_requested" not in st.session_state:
        st.session_state.location_requested = False

    if st.button(
        "📍 CAPTURE MY LOCATION",
        use_container_width=True
    ):
        st.session_state.location_requested = True
        st.rerun()

    if st.session_state.location_requested:

        if GEO_AVAILABLE:

            loc = streamlit_geolocation()

            if loc and loc.get("latitude") is not None:

                data = {
                    "incident_id": st.session_state.incident_id,
                    "timestamp": now(),
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                    "accuracy": loc.get("accuracy")
                }

                fp = p / f"{st.session_state.incident_id}_location.json"

                fp.write_text(
                    json.dumps(data, indent=2),
                    encoding="utf-8"
                )

                if not any(
                    x["type"] == "LOCATION"
                    for x in st.session_state.evidence
                ):
                    add_evidence(
                        "LOCATION",
                        fp,
                        f"GPS: {data['latitude']}, {data['longitude']}"
                    )

                st.success("✅ Location captured successfully.")

                st.write(
                    f"📍 Latitude: `{data['latitude']}`"
                )

                st.write(
                    f"📍 Longitude: `{data['longitude']}`"
                )

                if data.get("accuracy") is not None:
                    st.write(
                        f"🎯 Accuracy: `{data['accuracy']} meters`"
                    )

                try:
                    st.map({
                        "latitude": [data["latitude"]],
                        "longitude": [data["longitude"]]
                    })
                except Exception:
                    pass

            else:
                st.info(
                    "📍 Please allow location permission in your browser. "
                    "After allowing it, click **CAPTURE MY LOCATION** again."
                )

        else:
            st.error(
                "Location component is unavailable. "
                "Make sure `streamlit-geolocation` is in requirements.txt."
            )

    # =========================
    # VIDEO
    # =========================
    st.divider()
    st.header("🎥 Emergency Video Capture")

    if VIDEO_AVAILABLE:
        st.info("🎥 Click START below to activate the emergency camera.")

        rtc = RTCConfiguration({
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302"
                    ]
                }
            ]
        })

        ctx = webrtc_streamer(
            key="safeher-video-" + st.session_state.incident_id,
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc,
            media_stream_constraints={
                "video": True,
                "audio": True
            },
            async_processing=True,
            media_toggle_controls=True
        )

        if ctx.state.playing:
            st.success("🔴 Emergency camera is ACTIVE.")
        else:
            st.warning("⏸️ Camera is waiting to be started.")

        st.caption(
            "When the browser asks for camera/microphone permission, select Allow."
        )

    else:
        st.error(
            "Video component unavailable. Check streamlit-webrtc and av in requirements.txt."
        )

    else:
        st.warning(
            "Video component unavailable. "
            "Install streamlit-webrtc and av."
        )

st.header("📸 Emergency Evidence Capture")

if not st.session_state.incident_active:
    st.info("Activate SOS first.")

else:
    p = folder()

    # =========================
    # SNAPSHOT
    # =========================
    st.subheader("📷 Emergency Snapshot")

    snap = st.camera_input(
        "Take emergency snapshot",
        key="camera"
    )

    if snap is not None:
        fp = p / f"{st.session_state.incident_id}_snapshot_{datetime.now():%Y%m%d_%H%M%S}.jpg"

        fp.write_bytes(snap.getvalue())

        add_evidence(
            "SNAPSHOT",
            fp,
            "Camera snapshot captured during active incident."
        )

        st.success("✅ Snapshot saved successfully.")

    # =========================
    # LOCATION
    # =========================
    st.divider()

    st.subheader("📍 Emergency Location")

    if "location_requested" not in st.session_state:
        st.session_state.location_requested = False

    if st.button(
        "📍 CAPTURE MY LOCATION",
        use_container_width=True
    ):
        st.session_state.location_requested = True
        st.rerun()

    if st.session_state.location_requested:

        if GEO_AVAILABLE:

            loc = streamlit_geolocation()

            if loc and loc.get("latitude") is not None:

                data = {
                    "incident_id": st.session_state.incident_id,
                    "timestamp": now(),
                    "latitude": loc.get("latitude"),
                    "longitude": loc.get("longitude"),
                    "accuracy": loc.get("accuracy")
                }

                fp = p / f"{st.session_state.incident_id}_location.json"

                fp.write_text(
                    json.dumps(data, indent=2),
                    encoding="utf-8"
                )

                if not any(
                    x["type"] == "LOCATION"
                    for x in st.session_state.evidence
                ):
                    add_evidence(
                        "LOCATION",
                        fp,
                        f"GPS: {data['latitude']}, {data['longitude']}"
                    )

                st.success("✅ Location captured successfully.")

                st.write(
                    f"📍 Latitude: `{data['latitude']}`"
                )

                st.write(
                    f"📍 Longitude: `{data['longitude']}`"
                )

                if data.get("accuracy") is not None:
                    st.write(
                        f"🎯 Accuracy: `{data['accuracy']} meters`"
                    )

                try:
                    st.map({
                        "latitude": [data["latitude"]],
                        "longitude": [data["longitude"]]
                    })
                except Exception:
                    pass

            else:
                st.info(
                    "📍 Please allow location permission in your browser. "
                    "After allowing it, click **CAPTURE MY LOCATION** again."
                )

        else:
            st.error(
                "Location component is unavailable. "
                "Make sure `streamlit-geolocation` is in requirements.txt."
            )

    # =========================
    # VIDEO
    # =========================
    st.divider()

    st.header("🎥 Emergency Video Capture")

    if VIDEO_AVAILABLE:

        st.info(
            "🎥 Click START below to activate the emergency camera."
        )

        rtc = RTCConfiguration({
            "iceServers": [
                {
                    "urls": [
                        "stun:stun.l.google.com:19302"
                    ]
                }
            ]
        })

        ctx = webrtc_streamer(
            key="safeher-video-" + st.session_state.incident_id,
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc,
            media_stream_constraints={
                "video": True,
                "audio": True
            },
            async_processing=True,
            media_toggle_controls=True
        )

        if ctx.state.playing:
            st.success("🔴 Emergency camera is ACTIVE.")
        else:
            st.warning("⏸️ Camera is waiting to be started.")

        st.caption(
            "When the browser asks for camera/microphone permission, "
            "select Allow."
        )

    else:
        st.error(
            "Video component unavailable. "
            "Check streamlit-webrtc and av in requirements.txt."
        )


st.header("🛡️ Evidence Captured")

if not st.session_state.evidence:
    st.info("No completed evidence actions yet.")

else:
    for i, item in enumerate(
        reversed(st.session_state.evidence),
        1
    ):
        st.markdown(
            f'''
            <div class="evidence">
                <b>#{i} {item["type"]}</b><br>
                🕒 {item["timestamp"]}<br>
                🆔 {item["incident_id"]}<br>
                📝 {item["description"]}<br>
                📁 {item["file"]}
            </div>
            ''',
            unsafe_allow_html=True
        )


st.header("🤖 AI Safety Classification")

desc = st.text_area(
    "Describe the situation",
    placeholder="Example: Someone has been following me for the last 10 minutes..."
)

if st.button("🤖 Analyze Safety Situation"):
    st.session_state.ai_result = classify(desc)

if st.session_state.ai_result:

    risk, ex = st.session_state.ai_result

    if risk == "HIGH RISK":
        st.error(f"🚨 {risk}: {ex}")

    elif risk == "MEDIUM RISK":
        st.warning(f"⚠️ {risk}: {ex}")

    else:
        st.success(f"🟢 {risk}: {ex}")


st.header("⚙️ Incident Controls")

if st.session_state.incident_active:

    if st.button("🛑 End Incident"):
        st.session_state.incident_active = False
        st.session_state.sos_message = (
            "Incident ended. Evidence remains saved."
        )
        st.rerun()


if st.session_state.incident_id:

    mf = folder() / "evidence_manifest.json"

    if mf.exists():

        st.download_button(
            "⬇️ Download Incident Manifest",
            mf.read_bytes(),
            file_name=f"{st.session_state.incident_id}_manifest.json",
            mime="application/json"
        )

with st.expander("👮 Responder Dashboard"):
    st.write("Authorized responders can open the incident evidence dashboard.")

    if st.button("👮 Open Responder Dashboard", use_container_width=True):
        st.query_params["mode"] = "responder"
        st.rerun()
with st.expander("🔧 Technical Workflow"):
    st.markdown("""
**SOS → Incident ID → incident-specific folder → snapshot/location evidence → emergency camera stream → AI risk classification → responder dashboard.**

This is a college prototype. Browser camera/GPS access requires user permission. Colab/local storage is temporary; production deployment should use persistent encrypted storage, real authentication, HTTPS and audit logging.
""")

st.markdown('<div class="footer">🌸 SafeHer AI • Women Safety & Emergency Evidence Prototype</div>',unsafe_allow_html=True)
