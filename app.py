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
# COMPLETE LIGHT UI
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {
        background: #fff7fc !important;
        color: #333333 !important;
    }

    .main {
        background: #fff7fc !important;
    }

    /* EVERYTHING TEXT */

    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp div,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #333333;
    }

    /* ========================================================
       HEADINGS
       ======================================================== */

    h1, h2, h3, h4, h5, h6 {
        color: #333333 !important;
    }

    /* ========================================================
       HERO
       ======================================================== */

    .safeher-hero {
        background: linear-gradient(
            135deg,
            #ff5fa2,
            #c56cff,
            #7b61ff
        ) !important;

        padding: 30px;
        border-radius: 25px;
        text-align: center;
        margin-bottom: 25px;

        box-shadow:
            0 10px 30px
            rgba(190, 80, 160, 0.18);
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
        border: 2px solid #ff8fbd;
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 20px;
    }

    .incident-box,
    .incident-box * {
        color: #333333 !important;
    }

    /* ========================================================
       CARDS
       ======================================================== */

    .safeher-card {
        background: #ffffff !important;
        border-radius: 20px;
        padding: 22px;
        margin: 15px 0;
        box-shadow:
            0 5px 18px
            rgba(130, 80, 140, 0.08);
    }

    .safeher-card,
    .safeher-card * {
        color: #333333 !important;
    }

    /* ========================================================
       TEXT AREA
       ======================================================== */

    [data-testid="stTextArea"] textarea {
        background: #ffffff !important;
        color: #222222 !important;
        border: 2px solid #e5c9dc !important;
        border-radius: 12px !important;
        caret-color: #222222 !important;
    }

    [data-testid="stTextArea"] textarea::placeholder {
        color: #777777 !important;
        opacity: 1 !important;
    }

    [data-testid="stTextArea"] label {
        color: #333333 !important;
    }

    /* ========================================================
       TEXT INPUTS
       ======================================================== */

    [data-testid="stTextInput"] input {
        background: #ffffff !important;
        color: #222222 !important;
        border: 2px solid #e5c9dc !important;
    }

    /* ========================================================
       ALL BUTTONS
       ======================================================== */

    .stButton > button {
        background: #ffffff !important;
        color: #333333 !important;
        border: 2px solid #e4b8d2 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        min-height: 45px !important;
    }

    .stButton > button:hover {
        background: #fff0f7 !important;
        color: #222222 !important;
        border-color: #ff69a6 !important;
    }

    /* PRIMARY SOS */

    .stButton > button[kind="primary"] {
        background: linear-gradient(
            135deg,
            #ff4f91,
            #d95cff
        ) !important;

        color: #ffffff !important;
        border: none !important;
    }

    .stButton > button[kind="primary"]:hover {
        color: #ffffff !important;
    }

    /* ========================================================
       RESPONDER BUTTON
       ======================================================== */

    .responder-button {
        background: linear-gradient(
            135deg,
            #ff5fa2,
            #c56cff
        ) !important;

        color: #ffffff !important;

        border-radius: 14px;

        padding: 14px 20px;

        text-align: center;

        font-size: 16px;

        font-weight: 700;

        margin: 10px 0;
    }

    /* ========================================================
       CAMERA INPUT
       ======================================================== */

    [data-testid="stCameraInput"] {
        background: #ffffff !important;
        border: 2px solid #ead1df !important;
        border-radius: 15px !important;
        padding: 10px !important;
    }

    [data-testid="stCameraInput"] * {
        color: #333333 !important;
    }

    /* Camera buttons */

    [data-testid="stCameraInput"] button {
        background: #ffffff !important;
        color: #333333 !important;
        border: 2px solid #e4b8d2 !important;
    }

    /* ========================================================
       GEOLOCATION COMPONENT
       ======================================================== */

    [data-testid="stCustomComponentV1"] {
        background: #ffffff !important;
        color: #333333 !important;
    }

    /* ========================================================
       METRICS
       ======================================================== */

    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 2px solid #ead1df !important;
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
       INFO / SUCCESS / WARNING / ERROR
       ======================================================== */

    [data-testid="stAlert"] {
        color: #333333 !important;
    }

    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span {
        color: #333333 !important;
    }

    /* ========================================================
       EVIDENCE
       ======================================================== */

    .evidence-box {
        background: #ffffff !important;

        border-left: 5px solid #ff69a6;

        border-radius: 14px;

        padding: 14px;

        margin: 10px 0;

        box-shadow:
            0 4px 14px
            rgba(120, 70, 130, 0.08);
    }

    .evidence-box,
    .evidence-box * {
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

    [data-testid="stExpander"] * {
        color: #333333 !important;
    }

    /* ========================================================
       CODE / RESPONDER LINK
       ======================================================== */

    code {
        color: #333333 !important;
        background: #f5eaf2 !important;
    }

    /* ========================================================
       CAPTION
       ======================================================== */

    [data-testid="stCaptionContainer"] {
        color: #666666 !important;
    }

    [data-testid="stCaptionContainer"] * {
        color: #666666 !important;
    }

    /* ========================================================
       DIVIDER
       ======================================================== */

    hr {
        border-color: #ead1df !important;
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
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def clean_filename(value):
    return re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        str(value)
    )


def get_incident_folder():

    if not st.session_state.incident_id:
        return BASE_DIR

    path = (
        BASE_DIR
        / clean_filename(
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
            current_time(),

        "evidence":
            st.session_state.evidence
    }

    file_path = (
        get_incident_folder()
        / "evidence_manifest.json"
    )

    file_path.write_text(
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
        "timestamp": current_time(),
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
        current_time()
    )

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

    if any(
        word in text
        for word in high_risk
    ):

        return (
            "HIGH RISK",
            "The description contains indicators of a potentially immediate safety threat."
        )

    if any(
        word in text
        for word in medium_risk
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
            <h1>🛡️ SafeHer AI</h1>
            <p>
                Authorized Responder Dashboard
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    responder_key = st.query_params.get(
        "key"
    )

    if responder_key != "safeher-demo":

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

                for item in evidence:

                    st.markdown(
                        f"""
                        <div class="evidence-box">

                        <b>
                            {item.get("type", "")}
                        </b>
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
        key="responder_back_dashboard"
    ):

        st.query_params.clear()
        st.rerun()

    st.stop()


# ============================================================
# HERO
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
# EVIDENCE
# ============================================================

st.header(
    "📸 Emergency Evidence Capture"
)


if not st.session_state.incident_active:

    st.info(
        "Activate SOS first to enable evidence capture."
    )


else:

    evidence_folder = (
        get_incident_folder()
    )


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
            key="safeher_final_snapshot"
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

    st.caption(
        "Capture your current GPS location."
    )

    if st.button(
        "📍 CAPTURE MY LOCATION",
        use_container_width=True,
        key="safeher_final_location"
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

                exists = any(
                    item["type"] == "LOCATION"
                    for item in
                    st.session_state.evidence
                )

                if not exists:

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

    st.caption(
        "Camera recording is available below."
    )

    if VIDEO_AVAILABLE:

        st.info(
            "🎥 Press START below to activate the camera."
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
                "safeher_final_video_"
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
            "Camera only. Microphone permission is not requested."
        )

    else:

        st.error(
            "Video component unavailable. "
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
    key="safeher_final_ai"
)


if st.button(
    "🤖 ANALYZE SAFETY SITUATION",
    key="safeher_final_ai_button"
):

    if description.strip():

        st.session_state.ai_result = (
            classify_situation(
                description
            )
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
        key="safeher_final_end"
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
            "⬇️ DOWNLOAD INCIDENT MANIFEST",
            manifest_file.read_bytes(),
            file_name=(
                st.session_state.incident_id
                + "_manifest.json"
            ),
            mime="application/json",
            key="safeher_final_download"
        )


# ============================================================
# RESPONDER ACCESS
# ============================================================

st.divider()

st.header(
    "🛡️ Responder Access"
)

st.markdown(
    """
    <div class="safeher-card">

        <p>
            Authorized responders can access the
            SafeHer emergency evidence dashboard.
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


if st.button(
    "🛡️ OPEN RESPONDER DASHBOARD",
    use_container_width=True,
    key="safeher_final_responder"
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
