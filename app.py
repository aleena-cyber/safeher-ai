import streamlit as st
from pathlib import Path
from datetime import datetime
import json
import uuid
import re

# ============================================================
# OPTIONAL PACKAGES
# ============================================================

try:
    from streamlit_geolocation import streamlit_geolocation
    GEO_AVAILABLE = True
except Exception:
    GEO_AVAILABLE = False

try:
    from streamlit_webrtc import (
        webrtc_streamer,
        WebRtcMode,
        RTCConfiguration
    )
    VIDEO_AVAILABLE = True
except Exception:
    VIDEO_AVAILABLE = False


# ============================================================
# PAGE
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
BASE_DIR.mkdir(exist_ok=True)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background: linear-gradient(
            135deg,
            #fff5fb,
            #fdf7ff,
            #f7f2ff
        );
    }

    /* NORMAL TEXT */

    .stApp p,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #333333 !important;
    }

    /* HERO */

    .safeher-hero {
        background: linear-gradient(
            135deg,
            #ff5fa2,
            #c56cff,
            #7b61ff
        );
        padding: 28px;
        border-radius: 24px;
        text-align: center;
        margin-bottom: 22px;
    }

    .safeher-hero h1 {
        color: white !important;
        font-size: 42px;
        margin: 0;
    }

    .safeher-hero p {
        color: white !important;
        font-size: 17px;
        margin-top: 8px;
    }

    /* INCIDENT */

    .incident-box {
        background: #fff0f6;
        border: 2px solid #ff8fbd;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 20px;
    }

    .incident-box * {
        color: #333333 !important;
    }

    /* EVIDENCE */

    .evidence-box {
        background: white;
        border-left: 5px solid #ff69a6;
        border-radius: 14px;
        padding: 14px;
        margin: 10px 0;
        box-shadow: 0 4px 14px rgba(120,70,130,0.08);
    }

    .evidence-box * {
        color: #333333 !important;
    }

    /* TEXT AREA */

    textarea,
    input {
        color: #333333 !important;
        background: white !important;
    }

    /* BUTTON */

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

defaults = {
    "incident_active": False,
    "incident_id": None,
    "incident_started": None,
    "sos_message": "",
    "evidence": [],
    "location_requested": False,
    "ai_result": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# FUNCTIONS
# ============================================================

def current_time():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def clean_name(value):
    return re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        str(value)
    )


def incident_folder():

    if not st.session_state.incident_id:
        return BASE_DIR

    path = (
        BASE_DIR
        / clean_name(
            st.session_state.incident_id
        )
    )

    path.mkdir(
        parents=True,
        exist_ok=True
    )

    return path


def save_manifest():

    if not st.session_state.incident_id:
        return

    data = {
        "incident_id": st.session_state.incident_id,
        "incident_started": st.session_state.incident_started,
        "updated": current_time(),
        "evidence": st.session_state.evidence
    }

    file_path = (
        incident_folder()
        / "evidence_manifest.json"
    )

    file_path.write_text(
        json.dumps(
            data,
            indent=2
        ),
        encoding="utf-8"
    )


def record_evidence(
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


def activate_sos():

    incident_id = (
        "SH-"
        + datetime.now().strftime("%Y%m%d-%H%M%S")
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    st.session_state.incident_active = True
    st.session_state.incident_id = incident_id
    st.session_state.incident_started = current_time()
    st.session_state.sos_message = (
        "SOS ACTIVATED — evidence collection is active."
    )
    st.session_state.evidence = []
    st.session_state.location_requested = False
    st.session_state.ai_result = None

    incident_folder()
    save_manifest()


def classify_situation(text):

    text = text.lower()

    high_risk = [
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

    medium_risk = [
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

    if any(word in text for word in high_risk):
        return (
            "HIGH RISK",
            "The description contains indicators of a potentially immediate safety threat."
        )

    if any(word in text for word in medium_risk):
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

if st.query_params.get("mode") == "responder":

    st.markdown(
        """
        <div class="safeher-hero">
            <h1>🛡️ SafeHer AI</h1>
            <p>Authorized Responder Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    key = st.query_params.get("key", "")

    if key != "safeher-demo":
        st.error("🔐 Unauthorized responder access.")
        st.stop()

    st.success("✅ Responder access granted.")

    st.header("🚨 Incident Evidence")

    folders = sorted(
        [
            x for x in BASE_DIR.iterdir()
            if x.is_dir()
        ],
        reverse=True
    )

    if not folders:

        st.info(
            "No incident evidence has been recorded yet."
        )

    for folder_path in folders:

        manifest = (
            folder_path
            / "evidence_manifest.json"
        )

        if not manifest.exists():
            continue

        try:
            data = json.loads(
                manifest.read_text(
                    encoding="utf-8"
                )
            )
        except Exception:
            data = {}

        incident_id = data.get(
            "incident_id",
            folder_path.name
        )

        with st.expander(
            f"🚨 {incident_id}"
        ):

            st.write(
                "🕒 Started:",
                data.get(
                    "incident_started",
                    "Unknown"
                )
            )

            evidence = data.get(
                "evidence",
                []
            )

            if not evidence:
                st.info(
                    "No evidence captured."
                )

            for item in evidence:

                st.markdown(
                    f"""
                    <div class="evidence-box">
                    <b>{item.get("type", "")}</b><br>
                    🕒 {item.get("timestamp", "")}<br>
                    🆔 {item.get("incident_id", "")}<br>
                    📝 {item.get("description", "")}<br>
                    📁 {item.get("file", "")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.stop()


# ============================================================
# MAIN DASHBOARD
# ============================================================

st.markdown(
    """
    <div class="safeher-hero">
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
        <div class="incident-box">
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
    key="main_sos_button"
):

    if not st.session_state.incident_active:

        activate_sos()
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
# EVIDENCE
# ============================================================

st.header(
    "📸 Emergency Evidence Capture"
)

if not st.session_state.incident_active:

    st.info(
        "Activate SOS first."
    )

else:

    path = incident_folder()


    # ========================================================
    # SNAPSHOT
    # ========================================================

    st.subheader(
        "📷 Emergency Snapshot"
    )

    st.caption(
        "Use the camera below to capture emergency evidence."
    )

    left, center, right = st.columns(
        [1, 2, 1]
    )

    with center:

        snapshot = st.camera_input(
            "Take emergency snapshot",
            key="ONLY_SAFEHER_SNAPSHOT"
        )

    if snapshot is not None:

        file_path = (
            path
            / (
                st.session_state.incident_id
                + "_snapshot_"
                + datetime.now().strftime(
                    "%Y%m%d_%H%M%S"
                )
                + ".jpg"
            )
        )

        file_path.write_bytes(
            snapshot.getvalue()
        )

        record_evidence(
            "SNAPSHOT",
            file_path,
            "Emergency snapshot captured."
        )

        st.success(
            "✅ Snapshot saved."
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
        key="ONLY_SAFEHER_LOCATION"
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
                    path
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

                already_saved = any(
                    item["type"] == "LOCATION"
                    for item in st.session_state.evidence
                )

                if not already_saved:

                    record_evidence(
                        "LOCATION",
                        location_file,
                        (
                            f"GPS: "
                            f"{latitude}, "
                            f"{longitude}"
                        )
                    )

                st.success(
                    "✅ Location captured successfully."
                )

                c1, c2 = st.columns(2)

                with c1:
                    st.metric(
                        "📍 Latitude",
                        str(latitude)
                    )

                with c2:
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
                    "📍 Allow location permission in your "
                    "browser, then press the location button again."
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

        rtc = RTCConfiguration(
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

        video = webrtc_streamer(
            key=(
                "ONLY_SAFEHER_VIDEO_"
                + st.session_state.incident_id
            ),
            mode=WebRtcMode.SENDRECV,
            rtc_configuration=rtc,
            media_stream_constraints={
                "video": True,
                "audio": False
            },
            async_processing=True,
            media_toggle_controls=True
        )

        if video.state.playing:

            st.success(
                "🔴 Emergency camera is ACTIVE."
            )

        else:

            st.warning(
                "⏸️ Camera is waiting to be started."
            )

        st.caption(
            "Camera only is used. Microphone access is disabled."
        )

    else:

        st.error(
            "Video component unavailable. "
            "Check streamlit-webrtc and av."
        )


# ============================================================
# EVIDENCE LIST
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
        reversed(
            st.session_state.evidence
        ),
        1
    ):

        st.markdown(
            f"""
            <div class="evidence-box">
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
# AI CLASSIFICATION
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
    key="ONLY_SAFEHER_AI_TEXT"
)

if st.button(
    "🤖 Analyze Safety Situation",
    key="ONLY_SAFEHER_AI_BUTTON"
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
        "🛑 End Incident",
        key="ONLY_SAFEHER_END"
    ):

        st.session_state.incident_active = False

        st.session_state.sos_message = (
            "Incident ended. Evidence remains saved."
        )

        save_manifest()

        st.rerun()


if st.session_state.incident_id:

    manifest = (
        incident_folder()
        / "evidence_manifest.json"
    )

    if manifest.exists():

        st.download_button(
            "⬇️ Download Incident Manifest",
            manifest.read_bytes(),
            file_name=(
                st.session_state.incident_id
                + "_manifest.json"
            ),
            mime="application/json",
            key="ONLY_SAFEHER_DOWNLOAD"
        )


# ============================================================
# RESPONDER ACCESS
# ============================================================

st.divider()

st.header(
    "🛡️ Responder Access"
)

st.info(
    "Authorized responders can open the SafeHer "
    "emergency evidence dashboard."
)

st.code(
    "?mode=responder&key=safeher-demo"
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌸 SafeHer AI — Personal safety technology demonstration."
)
