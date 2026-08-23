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
    from streamlit_webrtc import (
        webrtc_streamer,
        WebRtcMode,
        RTCConfiguration
    )
    VIDEO_AVAILABLE = True
except Exception:
    VIDEO_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SafeHer AI",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# STORAGE
# ============================================================

BASE_DIR = Path("safeher_evidence")
BASE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LIGHT THEME
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       FORCE LIGHT COLOR SCHEME
       ======================================================== */

    :root {
        color-scheme: light !important;
    }

    html {
        color-scheme: light !important;
        background: #fff7fc !important;
    }

    body {
        background: #fff7fc !important;
        color: #333333 !important;
    }

    [data-testid="stAppViewContainer"] {
        background: #fff7fc !important;
    }

    [data-testid="stAppViewBlockContainer"] {
        background: #fff7fc !important;
    }

    [data-testid="stMain"] {
        background: #fff7fc !important;
    }

    .main {
        background: #fff7fc !important;
    }

    .block-container {
        background: #fff7fc !important;
    }


    /* ========================================================
       NORMAL TEXT
       ======================================================== */

    h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }

    p {
        color: #333333 !important;
    }

    label {
        color: #333333 !important;
    }


    /* ========================================================
       HERO
       ======================================================== */

    .safeher-hero {
        background: linear-gradient(
            135deg,
            #ff5a9f 0%,
            #d15cff 100%
        ) !important;

        border-radius: 25px;
        padding: 30px;
        margin-bottom: 25px;
        text-align: center;

        box-shadow:
            0 10px 30px
            rgba(180, 80, 160, 0.15);
    }

    .safeher-hero h1 {
        color: #ffffff !important;
        font-size: 42px !important;
        margin: 0 !important;
    }

    .safeher-hero p {
        color: #ffffff !important;
        font-size: 17px !important;
        margin-top: 8px !important;
    }


    /* ========================================================
       INCIDENT BOX
       ======================================================== */

    .incident-box {
        background: #fff0f6 !important;
        border: 2px solid #ff9bc4 !important;
        border-radius: 17px !important;
        padding: 16px !important;
        margin-bottom: 20px !important;
    }

    .incident-box,
    .incident-box b {
        color: #333333 !important;
    }


    /* ========================================================
       WHITE CARDS
       ======================================================== */

    .safeher-card {
        background: #ffffff !important;
        border: 1px solid #efd7e4 !important;
        border-radius: 18px !important;
        padding: 20px !important;
        margin: 15px 0 !important;

        box-shadow:
            0 5px 18px
            rgba(120, 60, 120, 0.07) !important;
    }

    .safeher-card h2,
    .safeher-card p {
        color: #333333 !important;
    }


    /* ========================================================
       TEXT AREA
       ======================================================== */

    [data-testid="stTextArea"] {
        background: #ffffff !important;
    }

    [data-testid="stTextArea"] label {
        color: #333333 !important;
    }

    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #222222 !important;
        -webkit-text-fill-color: #222222 !important;

        border: 2px solid #dfbfd2 !important;
        border-radius: 12px !important;

        caret-color: #222222 !important;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #777777 !important;
        -webkit-text-fill-color: #777777 !important;
        opacity: 1 !important;
    }


    /* ========================================================
       ALL NORMAL BUTTONS
       ======================================================== */

    .stButton > button {
        background: #ffffff !important;

        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;

        border: 2px solid #dfb8ce !important;
        border-radius: 12px !important;

        font-weight: 700 !important;
        min-height: 45px !important;
    }

    .stButton > button p {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }

    .stButton > button span {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }

    .stButton > button:hover {
        background: #fff0f7 !important;
        color: #222222 !important;
        border-color: #ff65a5 !important;
    }


    /* ========================================================
       PRIMARY SOS BUTTON
       ======================================================== */

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #ff4f91,
            #d35cff
        ) !important;

        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;

        border: none !important;
    }

    .stButton > button[kind="primary"] p,
    .stButton > button[kind="primary"] span {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }


    /* ========================================================
       DOWNLOAD BUTTON
       ======================================================== */

    .stDownloadButton > button {
        background: #ffffff !important;

        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;

        border: 2px solid #dfb8ce !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }

    .stDownloadButton > button p,
    .stDownloadButton > button span {
        color: #333333 !important;
        -webkit-text-fill-color: #333333 !important;
    }


    /* ========================================================
       CAMERA INPUT
       ======================================================== */

    [data-testid="stCameraInput"] {
        background: #ffffff !important;

        border: 2px solid #ead1df !important;
        border-radius: 15px !important;

        padding: 8px !important;
    }

    [data-testid="stCameraInput"] label {
        color: #333333 !important;
    }

    [data-testid="stCameraInput"] p {
        color: #333333 !important;
    }

    [data-testid="stCameraInput"] button {
        background: #ffffff !important;
        color: #333333 !important;
        border: 2px solid #dfb8ce !important;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {
        border-radius: 12px !important;
    }

    [data-testid="stAlert"] p {
        color: #333333 !important;
    }


    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #ead1df !important;
        border-radius: 14px !important;
        padding: 10px !important;
    }

    [data-testid="stMetricLabel"] {
        color: #666666 !important;
    }

    [data-testid="stMetricValue"] {
        color: #333333 !important;
    }


    /* ========================================================
       EXPANDERS
       ======================================================== */

    [data-testid="stExpander"] {
        background: #ffffff !important;
        border: 2px solid #ead1df !important;
        border-radius: 14px !important;
    }

    [data-testid="stExpander"] summary {
        color: #333333 !important;
    }

    [data-testid="stExpander"] p {
        color: #333333 !important;
    }


    /* ========================================================
       CAPTIONS
       ======================================================== */

    [data-testid="stCaptionContainer"] {
        color: #666666 !important;
    }

    [data-testid="stCaptionContainer"] p {
        color: #666666 !important;
    }


    /* ========================================================
       EVIDENCE BOX
       ======================================================== */

    .evidence-box {
        background: #ffffff !important;

        border: 1px solid #ead1df !important;
        border-left: 6px solid #ff69a6 !important;

        border-radius: 14px !important;

        padding: 16px !important;
        margin: 12px 0 !important;

        box-shadow:
            0 4px 14px
            rgba(120, 60, 120, 0.08) !important;
    }

    .evidence-box b {
        color: #b52f78 !important;
    }

    .evidence-box {
        color: #333333 !important;
    }


    /* ========================================================
       VIDEO AREA
       ======================================================== */

    /* Keep the surrounding video area light */
    [data-testid="stCustomComponentV1"] {
        background: #ffffff !important;
        border-radius: 15px !important;
    }

    /* Streamlit iframe */
    iframe {
        color-scheme: light !important;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {
        border-color: #ead1df !important;
    }


    /* ========================================================
       LINKS
       ======================================================== */

    a {
        color: #b52f78 !important;
    }


    /* ========================================================
       INFO / STATUS TEXT
       ======================================================== */

    [data-testid="stMarkdownContainer"] p {
        color: #333333 !important;
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

def now():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def safe_name(value):
    return re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        str(value)
    )


def folder():

    if not st.session_state.incident_id:
        return BASE_DIR

    path = (
        BASE_DIR
        / safe_name(
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
        "incident_id":
            st.session_state.incident_id,

        "incident_started":
            st.session_state.incident_started,

        "updated":
            now(),

        "evidence":
            st.session_state.evidence
    }

    manifest = (
        folder()
        / "evidence_manifest.json"
    )

    manifest.write_text(
        json.dumps(
            data,
            indent=2
        ),
        encoding="utf-8"
    )


def add_evidence(
    evidence_type,
    file_path,
    description
):

    item = {
        "type": evidence_type,

        "timestamp":
            now(),

        "incident_id":
            st.session_state.incident_id,

        "description":
            description,

        "file":
            str(file_path)
    }

    st.session_state.evidence.append(
        item
    )

    save_manifest()


def start_incident():

    incident_id = (
        "SH-"
        + datetime.now().strftime(
            "%Y%m%d-%H%M%S"
        )
        + "-"
        + uuid.uuid4().hex[:6].upper()
    )

    st.session_state.incident_id = (
        incident_id
    )

    st.session_state.incident_started = (
        now()
    )

    st.session_state.incident_active = True

    st.session_state.sos_message = (
        "SOS ACTIVATED — evidence collection is active."
    )

    st.session_state.evidence = []

    st.session_state.location_requested = False

    st.session_state.ai_result = None

    folder()

    save_manifest()


def classify(text):

    text = text.lower()

    high = [
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

    medium = [
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

    if any(
        word in text
        for word in high
    ):

        return (
            "HIGH RISK",
            "The description contains indicators of a potentially immediate safety threat."
        )

    if any(
        word in text
        for word in medium
    ):

        return (
            "MEDIUM RISK",
            "The description suggests a potentially unsafe situation."
        )

    return (
        "LOW RISK",
        "No strong high-risk indicators were detected."
    )


# ============================================================
# RESPONDER MODE
# ============================================================

if st.query_params.get("mode") == "responder":

    st.markdown(
        """
        <div class="safeher-hero">
            <h1>🌸 SafeHer AI</h1>
            <p>Authorized Responder Dashboard</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.query_params.get("key") != "safeher-demo":

        st.error(
            "🔐 Unauthorized responder access."
        )

        if st.button(
            "⬅️ Back to SafeHer AI",
            key="responder_unauthorized_back"
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

    incidents = []

    for item in BASE_DIR.iterdir():

        if item.is_dir():
            incidents.append(item)

    incidents = sorted(
        incidents,
        key=lambda x: x.name,
        reverse=True
    )

    if not incidents:

        st.info(
            "No incident evidence has been recorded yet."
        )

    for incident in incidents:

        manifest_file = (
            incident
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
            incident.name
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

            for item in evidence:

                st.markdown(
                    f"""
                    <div class="evidence-box">
                        <b>📌 {item.get("type", "")}</b>
                        <br>
                        🕒 {item.get("timestamp", "")}
                        <br>
                        🆔 {item.get("incident_id", "")}
                        <br>
                        📝 {item.get("description", "")}
                        <br>
                        📁 {item.get("file", "")}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    if st.button(
        "⬅️ Back to SafeHer AI",
        key="responder_dashboard_back"
    ):

        st.query_params.clear()
        st.rerun()

    st.stop()


# ============================================================
# MAIN HERO
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

            🚨 <b>INCIDENT ACTIVE</b>

            <br>

            🆔 {st.session_state.incident_id}

            <br>

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
    <div class="safeher-card">

        <h2>🚨 Emergency SOS</h2>

        <p>
            Creates a unique incident and enables
            evidence capture.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


if st.button(
    "🚨 ACTIVATE SOS",
    type="primary",
    use_container_width=True,
    key="sos_button"
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
        "Activate SOS first."
    )

else:

    incident_folder = folder()


    # ========================================================
    # SNAPSHOT
    # ========================================================

    st.subheader(
        "📷 Emergency Snapshot"
    )

    st.caption(
        "Capture an emergency snapshot."
    )

    left_col, camera_col, right_col = st.columns(
        [1, 2, 1]
    )

    with camera_col:

        snap = st.camera_input(
            "Take emergency snapshot",
            key="safeher_snapshot"
        )

    if snap is not None:

        snapshot_file = (
            incident_folder
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
            snap.getvalue()
        )

        add_evidence(
            "SNAPSHOT",
            snapshot_file,
            "Camera snapshot captured during active incident."
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

    st.caption(
        "Capture your current GPS location."
    )

    if st.button(
        "📍 CAPTURE MY LOCATION",
        use_container_width=True,
        key="safeher_location_button"
    ):

        st.session_state.location_requested = True
        st.rerun()


    if st.session_state.location_requested:

        if GEO_AVAILABLE:

            # IMPORTANT:
            # NO key parameter here.

            location = streamlit_geolocation()

            if (
                location
                and location.get("latitude") is not None
                and location.get("longitude") is not None
            ):

                latitude = location.get(
                    "latitude"
                )

                longitude = location.get(
                    "longitude"
                )

                accuracy = location.get(
                    "accuracy"
                )

                location_data = {
                    "incident_id":
                        st.session_state.incident_id,

                    "timestamp":
                        now(),

                    "latitude":
                        latitude,

                    "longitude":
                        longitude,

                    "accuracy":
                        accuracy
                }

                location_file = (
                    incident_folder
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

                location_exists = any(
                    item["type"] == "LOCATION"
                    for item in
                    st.session_state.evidence
                )

                if not location_exists:

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
                    "📍 Allow location access in your browser, "
                    "then press 📍 CAPTURE MY LOCATION again."
                )

        else:

            st.error(
                "📍 Location component unavailable. "
                "Check requirements.txt."
            )


    # ========================================================
    # VIDEO
    # ========================================================

    st.divider()

    st.subheader(
        "🎥 Emergency Video Capture"
    )

    st.caption(
        "Press START to activate the emergency camera."
    )

    if VIDEO_AVAILABLE:

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
                "safeher_video_"
                + str(
                    st.session_state.incident_id
                )
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
            "Camera only — microphone is disabled."
        )

    else:

        st.error(
            "🎥 Video component unavailable. "
            "Check streamlit-webrtc and av."
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
        reversed(
            st.session_state.evidence
        ),
        1
    ):

        st.markdown(
            f"""
            <div class="evidence-box">

                <b>
                    #{number} {item["type"]}
                </b>

                <br>

                🕒 {item["timestamp"]}

                <br>

                🆔 {item["incident_id"]}

                <br>

                📝 {item["description"]}

                <br>

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
    key="safeher_ai_description"
)


if st.button(
    "🤖 Analyze Safety Situation",
    key="safeher_ai_button"
):

    if description.strip():

        st.session_state.ai_result = (
            classify(description)
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
        key="safeher_end_incident"
    ):

        st.session_state.incident_active = False

        st.session_state.sos_message = (
            "Incident ended. Evidence remains saved."
        )

        save_manifest()

        st.rerun()


if st.session_state.incident_id:

    manifest = (
        folder()
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

            key="safeher_download_manifest"
        )


# ============================================================
# RESPONDER ACCESS
# ============================================================

st.divider()

st.header(
    "🛡️ Responder Access"
)

st.info(
    "Authorized responders can open the "
    "SafeHer emergency evidence dashboard."
)


if st.button(
    "🛡️ Open Responder Dashboard",
    use_container_width=True,
    key="safeher_responder_button"
):

    st.query_params["mode"] = "responder"
    st.query_params["key"] = "safeher-demo"

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🌸 SafeHer AI — Personal safety technology demonstration."
)
