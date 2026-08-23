import streamlit as st
from pathlib import Path
from datetime import datetime
import json
import uuid
import re

# ============================================================
# OPTIONAL COMPONENTS
# ============================================================

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


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SafeHer AI",
    page_icon="🌸",
    layout="wide"
)


# ============================================================
# STORAGE
# ============================================================

BASE_DIR = Path("safeher_evidence")
BASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #fff5fb 0%,
            #fdf7ff 50%,
            #f7f2ff 100%
        );
    }

    .stApp p,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp span {
        color: #333333 !important;
    }

    .hero {
        background: linear-gradient(
            135deg,
            #ff5fa2,
            #c56cff,
            #7b61ff
        );
        padding: 30px;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(190, 80, 160, 0.18);
    }

    .hero h1 {
        color: white !important;
        font-size: 42px;
        margin: 0;
    }

    .hero p {
        color: white !important;
        font-size: 17px;
        margin: 8px 0 0 0;
    }

    .incident {
        background: #fff0f6;
        border: 2px solid #ff8fbd;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 20px;
    }

    .incident * {
        color: #333333 !important;
    }

    .evidence {
        background: white;
        border-left: 5px solid #ff69a6;
        border-radius: 14px;
        padding: 14px;
        margin: 10px 0;
        box-shadow: 0 4px 14px rgba(120, 70, 130, 0.08);
    }

    .evidence * {
        color: #333333 !important;
    }

    textarea,
    input {
        color: #333333 !important;
        background: white !important;
    }

    .stButton button {
        font-weight: 700 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "incident_active" not in st.session_state:
    st.session_state.incident_active = False

if "incident_id" not in st.session_state:
    st.session_state.incident_id = None

if "incident_started" not in st.session_state:
    st.session_state.incident_started = None

if "sos_message" not in st.session_state:
    st.session_state.sos_message = ""

if "evidence" not in st.session_state:
    st.session_state.evidence = []

if "location_requested" not in st.session_state:
    st.session_state.location_requested = False

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None


# ============================================================
# FUNCTIONS
# ============================================================

def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def clean_filename(value):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", str(value))


def get_incident_folder():

    if not st.session_state.incident_id:
        return BASE_DIR

    path = BASE_DIR / clean_filename(
        st.session_state.incident_id
    )

    path.mkdir(parents=True, exist_ok=True)

    return path


def save_manifest():

    if not st.session_state.incident_id:
        return

    manifest = {
        "incident_id": st.session_state.incident_id,
        "incident_started": st.session_state.incident_started,
        "updated": current_time(),
        "evidence": st.session_state.evidence
    }

    manifest_file = (
        get_incident_folder()
        / "evidence_manifest.json"
    )

    manifest_file.write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8"
    )


def add_evidence(
    evidence_type,
    file_path,
    description
):

    item = {
        "type": evidence_type,
        "timestamp": current_time(),
        "incident_id": st.session_state.incident_id,
        "description": description,
        "file": str(file_path)
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

    st.session_state.incident_started = current_time()

    st.session_state.incident_active = True

    st.session_state.sos_message = (
        "SOS ACTIVATED — evidence collection is active."
    )

    st.session_state.evidence = []

    st.session_state.location_requested = False

    st.session_state.ai_result = None

    get_incident_folder()

    save_manifest()


def classify_situation(text):

    text = text.lower()

    high_risk_words = [
        "attack",
        "attacking",
        "weapon",
        "knife",
        "gun",
        "kidnap",
        "kidnapping",
        "assault",
        "threat",
        "threatening",
        "help me",
        "danger",
        "dangerous",
        "following me"
    ]

    medium_risk_words = [
        "stalking",
        "stalker",
        "unsafe",
        "scared",
        "suspicious",
        "harassment",
        "harassing",
        "stranger",
        "uncomfortable",
        "following"
    ]

    if any(word in text for word in high_risk_words):
        return (
            "HIGH RISK",
            "The description contains indicators of a potentially immediate safety threat."
        )

    if any(word in text for word in medium_risk_words):
        return (
            "MEDIUM RISK",
            "The description suggests a potentially unsafe situation."
        )

    return (
        "LOW RISK",
        "No strong high-risk indicators were detected."
    )


# ============================================================
# RESPONDER DASHBOARD
# ============================================================

query_mode = st.query_params.get("mode")
query_key = st.query_params.get("key")


if query_mode == "responder":

    st.markdown(
        """
        <div class="hero">
            <h1>🛡️ SafeHer AI</h1>
            <p>Authorized Responder Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if query_key != "safeher-demo":

        st.error(
            "🔐 Unauthorized responder access."
        )

        if st.button(
            "⬅️ Back to SafeHer AI",
            key="responder_back"
        ):

            st.query_params.clear()
            st.rerun()

        st.stop()


    st.success(
        "✅ Authorized responder access granted."
    )

    st.header(
        "🚨 Emergency Incidents"
    )

    incident_folders = sorted(
        [
            item
            for item in BASE_DIR.iterdir()
            if item.is_dir()
        ],
        reverse=True
    )

    if not incident_folders:

        st.info(
            "No incident evidence has been recorded yet."
        )

    else:

        for incident_folder in incident_folders:

            manifest_file = (
                incident_folder
                / "evidence_manifest.json"
            )

            if not manifest_file.exists():
                continue

            try:

                manifest = json.loads(
                    manifest_file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                manifest = {}

            incident_id = manifest.get(
                "incident_id",
                incident_folder.name
            )

            with st.expander(
                f"🚨 {incident_id}"
            ):

                st.write(
                    "🕒 Started:",
                    manifest.get(
                        "incident_started",
                        "Unknown"
                    )
                )

                evidence = manifest.get(
                    "evidence",
                    []
                )

                if not evidence:

                    st.info(
                        "No evidence captured."
                    )

                else:

                    for item in evidence:

                        st.markdown(
                            f"""
                            <div class="evidence">
                                <b>{item.get("type", "")}</b><br>
                                🕒 {item.get("timestamp", "")}<br>
                                🆔 {item.get("incident_id", "")}<br>
                                📝 {item.get("description", "")}<br>
                                📁 {item.get("file", "")}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

    if st.button(
        "⬅️ Back to SafeHer AI",
        key="responder_back_dashboard"
    ):

        st.query_params.clear()
        st.rerun()

    st.stop()


# ============================================================
# MAIN HERO
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🌸 SafeHer AI</h1>
        <p>
            AI-assisted personal safety,
            emergency evidence capture
            and responder support
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INCIDENT STATUS
# ============================================================

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


# ============================================================
# SOS
# ============================================================

st.markdown(
    """
    <div class="card">
        <h2>🚨 Emergency SOS</h2>
        <p>
            Creates a unique incident and enables
            emergency evidence capture.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


if st.button(
    "🚨 ACTIVATE SOS",
    type="primary",
    use_container_width=True,
    key="sos_main"
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


# ============================================================
# EMERGENCY EVIDENCE
# ============================================================

st.header(
    "📸 Emergency Evidence Capture"
)


if not st.session_state.incident_active:

    st.info(
        "Activate SOS first to enable evidence capture."
    )


else:

    evidence_folder = get_incident_folder()


    # ========================================================
    # SNAPSHOT
    # ========================================================

    st.subheader(
        "📷 Emergency Snapshot"
    )

    st.caption(
        "Capture a photo as emergency evidence."
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        snapshot = st.camera_input(
            "Take emergency snapshot",
            key="snapshot_unique_safeher"
        )


    if snapshot is not None:

        snapshot_file = (
            evidence_folder
            / (
                st.session_state.incident_id
                + "_snapshot_"
                + datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )
                + ".jpg"
            )
        )

        snapshot_file.write_bytes(
            snapshot.getvalue()
        )

        add_evidence(
            "SNAPSHOT",
            snapshot_file,
            "Emergency snapshot captured."
        )

        st.success(
            "✅ Snapshot saved successfully."
        )


    # ========================================================
    # LOCATION
    # ========================================================

    st.divider()

    st.subheader(
        "📍 Emergency Location"
    )

    if st.button(
        "📍 CAPTURE MY LOCATION",
        use_container_width=True,
        key="location_unique_safeher"
    ):

        st.session_state.location_requested = True
        st.rerun()


    if st.session_state.location_requested:

        if GEO_AVAILABLE:

            location = streamlit_geolocation()

            if (
                location
                and location.get("latitude") is not None
                and location.get("longitude") is not None
            ):

                latitude = location["latitude"]
                longitude = location["longitude"]
                accuracy = location.get("accuracy")

                location_data = {
                    "incident_id":
                        st.session_state.incident_id,
                    "timestamp":
                        current_time(),
                    "latitude":
                        latitude,
                    "longitude":
                        longitude,
                    "accuracy":
                        accuracy
                }

                location_file = (
                    evidence_folder
                    / (
                        st.session_state.incident_id
                        + "_location.json"
                    )
                )

                location_file.write_text(
                    json.dumps(
                        location_data,
                        indent=2
                    ),
                    encoding="utf-8"
                )

                already_recorded = any(
                    item["type"] == "LOCATION"
                    for item in st.session_state.evidence
                )

                if not already_recorded:

                    add_evidence(
                        "LOCATION",
                        location_file,
                        (
                            "GPS: "
                            + str(latitude)
                            + ", "
                            + str(longitude)
                        )
                    )

                st.success(
                    "✅ Location captured successfully."
                )

                col1, col2 = st.columns(2)

                with col1:

                    st.metric(
                        "📍 Latitude",
                        str(latitude)
                    )

                with col2:

                    st.metric(
                        "📍 Longitude",
                        str(longitude)
                    )

                if accuracy is not None:

                    st.caption(
                        f"🎯 Accuracy: {accuracy} meters"
                    )

                try:

                    st.map(
                        {
                            "latitude": [latitude],
                            "longitude": [longitude]
                        }
                    )

                except Exception:

                    pass

            else:

                st.info(
                    "📍 Please allow location permission "
                    "in your browser and click the button again."
                )

        else:

            st.error(
                "Location component unavailable. "
                "Check requirements.txt."
            )


    # ========================================================
    # VIDEO
    # ========================================================

    st.divider()

    st.subheader(
        "🎥 Emergency Video Capture"
    )


    if VIDEO_AVAILABLE:

        st.info(
            "🎥 Press START below to activate the emergency camera."
        )

        rtc_configuration = RTCConfiguration(
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
                "video_unique_safeher_"
                + st.session_state.incident_id
            ),
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc_configuration,
            media_stream_constraints={
                "video": True,
                "audio": False
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
            "Camera access only. Microphone is disabled."
        )

    else:

        st.error(
            "Video component unavailable. "
            "Check that streamlit-webrtc and av "
            "are in requirements.txt."
        )


# ============================================================
# EVIDENCE CAPTURED
# ============================================================

st.divider()

st.header(
    "🛡️ Evidence Captured"
)


if not st.session_state.evidence:

    st.info(
        "No completed evidence actions yet."
    )

else:

    for number, item in enumerate(
        reversed(st.session_state.evidence),
        1
    ):

        st.markdown(
            f"""
            <div class="evidence">
                <b>#{number} {item["type"]}</b><br>
                🕒 {item["timestamp"]}<br>
                🆔 {item["incident_id"]}<br>
                📝 {item["description"]}<br>
                📁 {item["file"]}
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# AI SAFETY CLASSIFICATION
# ============================================================

st.header(
    "🤖 AI Safety Classification"
)

description = st.text_area(
    "Describe the situation",
    placeholder=(
        "Example: Someone has been following me "
        "for the last 10 minutes..."
    ),
    key="ai_description_safeher"
)


if st.button(
    "🤖 Analyze Safety Situation",
    key="ai_button_safeher"
):

    if description.strip():

        st.session_state.ai_result = (
            classify_situation(description)
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


# ============================================================
# INCIDENT CONTROLS
# ============================================================

st.header(
    "⚙️ Incident Controls"
)


if st.session_state.incident_active:

    if st.button(
        "🛑 END INCIDENT",
        key="end_incident_safeher"
    ):

        st.session_state.incident_active = False

        st.session_state.sos_message = (
            "Incident ended. Evidence remains saved."
        )

        save_manifest()

        st.rerun()


if st.session_state.incident_id:

    manifest_file = (
        get_incident_folder()
        / "evidence_manifest.json"
    )

    if manifest_file.exists():

        st.download_button(
            "⬇️ Download Incident Manifest",
            manifest_file.read_bytes(),
            file_name=(
                st.session_state.incident_id
                + "_manifest.json"
            ),
            mime="application/json",
            key="manifest_download_safeher"
        )


# ============================================================
# RESPONDER ACCESS
# ============================================================

st.divider()

st.header(
    "🛡️ Responder Access"
)

st.info(
    "Authorized responders can access the "
    "SafeHer emergency evidence dashboard."
)


if st.button(
    "🛡️ OPEN RESPONDER DASHBOARD",
    use_container_width=True,
    key="responder_access_safeher"
):

    st.query_params.update(
        mode="responder",
        key="safeher-demo"
    )

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌸 SafeHer AI — Personal safety technology demonstration."
)
