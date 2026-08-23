import streamlit as st
import streamlit.components.v1 as components

from pathlib import Path
from datetime import datetime
import json
import uuid
import re

# Optional dependencies
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


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="SafeHer AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CONSTANTS
# =========================================================

BASE_DIR = Path("safeher_evidence")
BASE_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(135deg, #fff5fb 0%, #fdf7ff 45%, #f7f2ff 100%);
    }

    .hero {
        background: linear-gradient(
            135deg,
            #ff5fa2 0%,
            #c56cff 50%,
            #7b61ff 100%
        );
        padding: 30px;
        border-radius: 25px;
        text-align: center;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(190, 80, 160, 0.18);
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        margin: 0;
    }

    .incident {
        background: #fff0f6;
        border: 2px solid #ff8fbd;
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 20px;
    }

    .card {
        background: white;
        padding: 22px;
        border-radius: 20px;
        margin: 15px 0;
        box-shadow: 0 5px 18px rgba(130, 80, 140, 0.08);
    }

    .evidence {
        background: white;
        border-left: 5px solid #ff69a6;
        border-radius: 14px;
        padding: 14px;
        margin: 10px 0;
        box-shadow: 0 4px 14px rgba(120, 70, 130, 0.08);
    }

    .small-camera {
        max-width: 430px;
        margin-left: auto;
        margin-right: auto;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "incident_active": False,
    "incident_id": None,
    "incident_started": None,
    "sos_message": "",
    "evidence": [],
    "ai_result": None,
    "location_requested": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_filename(text):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(text))


def incident_folder():
    if not st.session_state.incident_id:
        return BASE_DIR

    folder = BASE_DIR / safe_filename(
        st.session_state.incident_id
    )

    folder.mkdir(parents=True, exist_ok=True)
    return folder


def save_manifest():
    if not st.session_state.incident_id:
        return

    folder = incident_folder()

    manifest = {
        "incident_id": st.session_state.incident_id,
        "incident_started": st.session_state.incident_started,
        "last_updated": now(),
        "evidence": st.session_state.evidence,
    }

    manifest_file = folder / "evidence_manifest.json"

    manifest_file.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )


def add_evidence(evidence_type, file_path, description):
    item = {
        "type": evidence_type,
        "timestamp": now(),
        "incident_id": st.session_state.incident_id,
        "description": description,
        "file": str(file_path),
    }

    st.session_state.evidence.append(item)
    save_manifest()


def start_incident():
    incident_id = (
        "SH-"
        + datetime.now().strftime("%Y%m%d-%H%M%S")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    st.session_state.incident_id = incident_id
    st.session_state.incident_started = now()
    st.session_state.incident_active = True
    st.session_state.sos_message = (
        "SOS ACTIVATED — evidence collection is active."
    )
    st.session_state.evidence = []
    st.session_state.location_requested = False
    st.session_state.ai_result = None

    incident_folder()
    save_manifest()


def end_incident():
    st.session_state.incident_active = False
    st.session_state.sos_message = (
        "Incident ended. Evidence remains saved."
    )
    save_manifest()


def classify_situation(description):
    text = description.lower()

    high_words = [
        "attack",
        "attacking",
        "kidnap",
        "kidnapping",
        "weapon",
        "knife",
        "gun",
        "threat",
        "threatening",
        "following me",
        "following",
        "abduction",
        "help me",
        "danger",
        "dangerous",
        "assault",
    ]

    medium_words = [
        "stalking",
        "scared",
        "unsafe",
        "suspicious",
        "harassment",
        "harassing",
        "stranger",
        "following",
        "uncomfortable",
    ]

    for word in high_words:
        if word in text:
            return (
                "HIGH RISK",
                "The description contains indicators of a potentially immediate safety threat."
            )

    for word in medium_words:
        if word in text:
            return (
                "MEDIUM RISK",
                "The description suggests a potentially unsafe situation. Consider contacting someone you trust or emergency services."
            )

    return (
        "LOW RISK",
        "No strong high-risk indicators were detected from the description."
    )


# =========================================================
# RESPONDER MODE
# =========================================================

query_params = st.query_params

if query_params.get("mode") == "responder":

    st.markdown(
        """
        <div class="hero">
            <h1>🛡️ SafeHer AI Responder Dashboard</h1>
            <p>Authorized incident evidence view</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    responder_key = query_params.get("key", "")

    if responder_key != "safeher-demo":
        st.error("🔐 Unauthorized responder access.")
        st.stop()

    st.success("✅ Responder demonstration access granted.")

    folders = sorted(
        [
            x for x in BASE_DIR.iterdir()
            if x.is_dir()
        ],
        reverse=True
    )

    if not folders:
        st.info("No incident evidence has been recorded yet.")
    else:
        st.subheader("📁 Recorded Incidents")

        for incident_dir in folders:

            manifest = incident_dir / "evidence_manifest.json"

            if manifest.exists():

                try:
                    data = json.loads(
                        manifest.read_text(
                            encoding="utf-8"
                        )
                    )
                except Exception:
                    data = {}

                with st.expander(
                    f"🚨 {data.get('incident_id', incident_dir.name)}"
                ):

                    st.write(
                        f"🕒 Started: "
                        f"{data.get('incident_started', 'Unknown')}"
                    )

                    evidence = data.get(
                        "evidence",
                        []
                    )

                    if evidence:

                        for item in evidence:
                            st.markdown(
                                f"""
                                <div class="evidence">
                                    <b>#{item.get('type', 'Evidence')}</b><br>
                                    🕒 {item.get('timestamp', '')}<br>
                                    🆔 {item.get('incident_id', '')}<br>
                                    📝 {item.get('description', '')}<br>
                                    📁 {item.get('file', '')}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    else:
                        st.info(
                            "No evidence has been recorded for this incident."
                        )

    st.stop()


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <h1>🌸 SafeHer AI</h1>
        <p>
            AI-assisted personal safety, emergency evidence capture
            and responder support
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# INCIDENT STATUS
# =========================================================

if st.session_state.incident_active:

    st.markdown(
        f"""
        <div class="incident">
            🚨 <b>INCIDENT ACTIVE</b><br>
            🆔 {st.session_state.incident_id}<br>
            🕒 {st.session_state.incident_started}
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.success(
        "🟢 SafeHer is ready. Press SOS if you feel unsafe."
    )


# =========================================================
# SOS
# =========================================================

st.markdown(
    """
    <div class="card">
        <h2>🚨 Emergency SOS</h2>
        <p>
            Creates a unique incident and enables emergency
            evidence collection.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button(
    "🚨 ACTIVATE SOS",
    type="primary",
    use_container_width=True,
    key="activate_sos_button"
):

    if not st.session_state.incident_active:

        start_incident()

        st.rerun()

    else:

        st.warning(
            "An incident is already active."
        )


if st.session_state.sos_message:

    st.warning(
        st.session_state.sos_message
    )


# =========================================================
# EMERGENCY EVIDENCE
# =========================================================

st.header("📸 Emergency Evidence Capture")

if not st.session_state.incident_active:

    st.info(
        "Activate SOS first to enable emergency evidence capture."
    )

else:

    evidence_path = incident_folder()

    # =====================================================
    # SNAPSHOT
    # =====================================================

    st.subheader("📷 Emergency Snapshot")

    st.markdown(
        '<div class="small-camera">',
        unsafe_allow_html=True
    )

    snapshot = st.camera_input(
        "Take emergency snapshot",
        key="emergency_snapshot_camera"
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True
    )

    if snapshot is not None:

        snapshot_file = (
            evidence_path
            / f"{st.session_state.incident_id}"
              f"_snapshot_"
              f"{datetime.now():%Y%m%d_%H%M%S}.jpg"
        )

        snapshot_file.write_bytes(
            snapshot.getvalue()
        )

        already_saved = any(
            item["type"] == "SNAPSHOT"
            and item["file"] == str(snapshot_file)
            for item in st.session_state.evidence
        )

        if not already_saved:

            add_evidence(
                "SNAPSHOT",
                snapshot_file,
                "Camera snapshot captured during active incident."
            )

            st.success(
                "✅ Snapshot saved successfully."
            )


    # =====================================================
    # LOCATION
    # =====================================================

    st.divider()

    st.subheader("📍 Emergency Location")

    if "location_requested" not in st.session_state:
        st.session_state.location_requested = False

    if st.button(
        "📍 CAPTURE MY LOCATION",
        use_container_width=True,
        key="capture_location_button"
    ):

        st.session_state.location_requested = True
        st.rerun()


    if st.session_state.location_requested:

        if GEO_AVAILABLE:

            location = streamlit_geolocation(
                key="safeher_location_component"
            )

            if (
                location
                and location.get("latitude") is not None
                and location.get("longitude") is not None
            ):

                location_data = {
                    "incident_id": st.session_state.incident_id,
                    "timestamp": now(),
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "accuracy": location.get("accuracy"),
                }

                location_file = (
                    evidence_path
                    / f"{st.session_state.incident_id}"
                      "_location.json"
                )

                location_file.write_text(
                    json.dumps(
                        location_data,
                        indent=2
                    ),
                    encoding="utf-8"
                )

                already_has_location = any(
                    item["type"] == "LOCATION"
                    for item in st.session_state.evidence
                )

                if not already_has_location:

                    add_evidence(
                        "LOCATION",
                        location_file,
                        (
                            f"GPS: "
                            f"{location_data['latitude']}, "
                            f"{location_data['longitude']}"
                        )
                    )

                st.success(
                    "✅ Location captured successfully."
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Latitude",
                        str(location_data["latitude"])
                    )

                with col2:
                    st.metric(
                        "Longitude",
                        str(location_data["longitude"])
                    )

                if location_data.get("accuracy") is not None:

                    st.caption(
                        f"🎯 Accuracy: "
                        f"{location_data['accuracy']} meters"
                    )

                try:

                    st.map(
                        {
                            "latitude": [
                                location_data["latitude"]
                            ],
                            "longitude": [
                                location_data["longitude"]
                            ],
                        }
                    )

                except Exception:
                    pass

            else:

                st.info(
                    "📍 Please allow location permission in your browser. "
                    "Then press **CAPTURE MY LOCATION** again."
                )

        else:

            st.error(
                "Location component is unavailable. "
                "Make sure `streamlit-geolocation` is in requirements.txt."
            )


    # =====================================================
    # VIDEO
    # =====================================================

    st.divider()

    st.subheader("🎥 Emergency Video Capture")

    if VIDEO_AVAILABLE:

        st.info(
            "🎥 Click START below to activate the emergency camera."
        )

        rtc_config = RTCConfiguration(
            {
                "iceServers": [
                    {
                        "urls": [
                            "stun:stun.l.google.com:19302"
                        ]
                    }
                ]
            }
        )

        video_context = webrtc_streamer(
            key=(
                "safeher_video_"
                + str(st.session_state.incident_id)
            ),
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_config,
            media_stream_constraints={
                "video": True,
                "audio": True
            },
            async_processing=True,
            media_toggle_controls=True
        )

        if video_context.state.playing:

            st.success(
                "🔴 Emergency camera is ACTIVE."
            )

        else:

            st.warning(
                "⏸️ Camera is waiting to be started."
            )

        st.caption(
            "When the browser asks for camera/microphone "
            "permission, select Allow."
        )

    else:

        st.error(
            "Video component unavailable. "
            "Check `streamlit-webrtc` and `av` in requirements.txt."
        )


# =========================================================
# EVIDENCE LIST
# =========================================================

st.divider()

st.header("🛡️ Evidence Captured")

if not st.session_state.evidence:

    st.info(
        "No completed evidence actions yet."
    )

else:

    for index, item in enumerate(
        reversed(st.session_state.evidence),
        1
    ):

        st.markdown(
            f"""
            <div class="evidence">
                <b>#{index} {item["type"]}</b><br>
                🕒 {item["timestamp"]}<br>
                🆔 {item["incident_id"]}<br>
                📝 {item["description"]}<br>
                📁 {item["file"]}
            </div>
            """,
            unsafe_allow_html=True
        )


# =========================================================
# AI SAFETY CLASSIFICATION
# =========================================================

st.header("🤖 AI Safety Classification")

description = st.text_area(
    "Describe the situation",
    placeholder=(
        "Example: Someone has been following me "
        "for the last 10 minutes..."
    ),
    key="safety_description"
)

if st.button(
    "🤖 Analyze Safety Situation",
    key="analyze_safety_button"
):

    if description.strip():

        st.session_state.ai_result = classify_situation(
            description
        )

    else:

        st.warning(
            "Please describe the situation first."
        )


if st.session_state.ai_result:

    risk, explanation = (
        st.session_state.ai_result
    )

    if risk == "HIGH RISK":

        st.error(
            f"🚨 {risk}: {explanation}"
        )

    elif risk == "MEDIUM RISK":

        st.warning(
            f"⚠️ {risk}: {explanation}"
        )

    else:

        st.success(
            f"🟢 {risk}: {explanation}"
        )


# =========================================================
# INCIDENT CONTROLS
# =========================================================

st.header("⚙️ Incident Controls")

if st.session_state.incident_active:

    if st.button(
        "🛑 End Incident",
        key="end_incident_button"
    ):

        end_incident()
        st.rerun()


if st.session_state.incident_id:

    manifest_file = (
        incident_folder()
        / "evidence_manifest.json"
    )

    if manifest_file.exists():

        st.download_button(
            "⬇️ Download Incident Manifest",
            data=manifest_file.read_bytes(),
            file_name=(
                f"{st.session_state.incident_id}"
                "_manifest.json"
            ),
            mime="application/json",
            key="download_manifest_button"
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌸 SafeHer AI — Safety technology demonstration."
)
