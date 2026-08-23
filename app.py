import streamlit as st
from pathlib import Path
from datetime import datetime
import json
import uuid
import re


# =========================================================
# OPTIONAL COMPONENTS
# =========================================================

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
# STORAGE
# =========================================================

BASE_DIR = Path("safeher_evidence")
BASE_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =========================
       MAIN PAGE
       ========================= */

    .stApp {
        background: linear-gradient(
            135deg,
            #fff5fb 0%,
            #fdf7ff 50%,
            #f7f2ff 100%
        );
    }

    /* Make normal text dark and readable */

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp small,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #333333 !important;
    }


    /* =========================
       HERO
       ========================= */

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

        box-shadow:
            0 10px 30px
            rgba(190, 80, 160, 0.18);
    }

    .hero h1,
    .hero p {
        color: white !important;
    }

    .hero h1 {
        font-size: 42px;
        margin-bottom: 8px;
    }

    .hero p {
        font-size: 17px;
        margin: 0;
    }


    /* =========================
       CARDS
       ========================= */

    .card {
        background: white;
        padding: 22px;
        border-radius: 20px;
        margin: 15px 0;

        box-shadow:
            0 5px 18px
            rgba(130, 80, 140, 0.08);
    }

    .card h2,
    .card p {
        color: #333333 !important;
    }


    /* =========================
       INCIDENT
       ========================= */

    .incident {
        background: #fff0f6;
        border: 2px solid #ff8fbd;
        border-radius: 18px;
        padding: 15px;
        margin-bottom: 20px;
        color: #333333 !important;
    }

    .incident * {
        color: #333333 !important;
    }


    /* =========================
       EVIDENCE
       ========================= */

    .evidence {
        background: white;
        border-left: 5px solid #ff69a6;
        border-radius: 14px;
        padding: 14px;
        margin: 10px 0;

        box-shadow:
            0 4px 14px
            rgba(120, 70, 130, 0.08);

        color: #333333 !important;
    }

    .evidence * {
        color: #333333 !important;
    }


    /* =========================
       INPUTS
       ========================= */

    .stTextArea textarea,
    .stTextInput input {
        color: #333333 !important;
        background: white !important;
    }

    .stTextArea textarea::placeholder,
    .stTextInput input::placeholder {
        color: #777777 !important;
    }


    /* =========================
       METRICS
       ========================= */

    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #333333 !important;
    }


    /* =========================
       CAPTIONS
       ========================= */

    [data-testid="stCaptionContainer"] {
        color: #555555 !important;
    }


    /* =========================
       BUTTONS
       ========================= */

    .stButton button {
        font-weight: 700 !important;
    }


    /* =========================
       DIVIDER
       ========================= */

    hr {
        border-color: #ead7e6 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# SESSION STATE
# =========================================================

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

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "location_requested" not in st.session_state:
    st.session_state.location_requested = False


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def now():
    return datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def safe_filename(value):
    return re.sub(
        r"[^A-Za-z0-9_.-]",
        "_",
        str(value)
    )


def folder():

    if not st.session_state.incident_id:
        return BASE_DIR

    incident_folder = (
        BASE_DIR
        / safe_filename(
            st.session_state.incident_id
        )
    )

    incident_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    return incident_folder


def save_manifest():

    if not st.session_state.incident_id:
        return

    manifest = {
        "incident_id":
            st.session_state.incident_id,

        "incident_started":
            st.session_state.incident_started,

        "last_updated":
            now(),

        "evidence":
            st.session_state.evidence
    }

    manifest_file = (
        folder()
        / "evidence_manifest.json"
    )

    manifest_file.write_text(
        json.dumps(
            manifest,
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
        "timestamp": now(),
        "incident_id":
            st.session_state.incident_id,
        "description": description,
        "file": str(file_path)
    }

    st.session_state.evidence.append(item)

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

    st.session_state.incident_id = incident_id

    st.session_state.incident_started = now()

    st.session_state.incident_active = True

    st.session_state.sos_message = (
        "SOS ACTIVATED — evidence collection is active."
    )

    st.session_state.evidence = []

    st.session_state.location_requested = False

    st.session_state.ai_result = None

    folder()

    save_manifest()


def end_incident():

    st.session_state.incident_active = False

    st.session_state.sos_message = (
        "Incident ended. Evidence remains saved."
    )

    save_manifest()


def classify(description):

    text = description.lower()

    high_words = [
        "attack",
        "attacking",
        "weapon",
        "knife",
        "gun",
        "kidnap",
        "kidnapping",
        "abduction",
        "assault",
        "threat",
        "threatening",
        "following me",
        "help me",
        "danger",
        "dangerous"
    ]

    medium_words = [
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

    for word in high_words:

        if word in text:

            return (
                "HIGH RISK",
                "The description contains indicators "
                "of a potentially immediate safety threat."
            )

    for word in medium_words:

        if word in text:

            return (
                "MEDIUM RISK",
                "The description suggests a "
                "potentially unsafe situation."
            )

    return (
        "LOW RISK",
        "No strong high-risk indicators were "
        "detected from the description."
    )


# =========================================================
# RESPONDER DASHBOARD
# =========================================================

if st.query_params.get("mode") == "responder":

    st.markdown(
        """
        <div class="hero">
            <h1>🛡️ SafeHer AI</h1>
            <p>
                Authorized Responder Dashboard
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    responder_key = st.query_params.get(
        "key",
        ""
    )

    if responder_key != "safeher-demo":

        st.error(
            "🔐 Unauthorized responder access."
        )

        st.stop()


    st.success(
        "✅ Responder access granted."
    )


    st.subheader(
        "🚨 Active / Recorded Incidents"
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

                data = json.loads(
                    manifest_file.read_text(
                        encoding="utf-8"
                    )
                )

            except Exception:

                data = {}


            incident_name = data.get(
                "incident_id",
                incident_folder.name
            )


            with st.expander(
                f"🚨 {incident_name}"
            ):

                st.write(
                    "🕒 Started: "
                    + str(
                        data.get(
                            "incident_started",
                            "Unknown"
                        )
                    )
                )


                evidence = data.get(
                    "evidence",
                    []
                )


                if not evidence:

                    st.info(
                        "No evidence recorded."
                    )


                else:

                    for item in evidence:

                        st.markdown(
                            f"""
                            <div class="evidence">
                                <b>
                                    {item.get("type", "Evidence")}
                                </b><br>
                                🕒 {item.get("timestamp", "")}<br>
                                🆔 {item.get("incident_id", "")}<br>
                                📝 {item.get("description", "")}<br>
                                📁 {item.get("file", "")}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


    st.stop()


# =========================================================
# MAIN HERO
# =========================================================

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


# =========================================================
# STATUS
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
            Creates a unique incident and enables
            emergency evidence collection.
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


# =========================================================
# EVIDENCE CAPTURE
# =========================================================

st.header(
    "📸 Emergency Evidence Capture"
)


if not st.session_state.incident_active:

    st.info(
        "Activate SOS first to enable evidence capture."
    )


else:

    evidence_folder = folder()


    # =====================================================
    # SNAPSHOT
    # =====================================================

    st.subheader(
        "📷 Emergency Snapshot"
    )


    # Center the camera so it doesn't occupy the
    # whole screen.

    empty_left, camera_column, empty_right = st.columns(
        [1, 2, 1]
    )


    with camera_column:

        snapshot = st.camera_input(
            "Take emergency snapshot",
            key="safeher_snapshot_camera"
        )


    if snapshot is not None:

        snapshot_file = (
            evidence_folder
            / (
                f"{st.session_state.incident_id}"
                f"_snapshot_"
                f"{datetime.now():%Y%m%d_%H%M%S}.jpg"
            )
        )

        snapshot_file.write_bytes(
            snapshot.getvalue()
        )

        add_evidence(
            "SNAPSHOT",
            snapshot_file,
            "Emergency snapshot captured during active incident."
        )

        st.success(
            "✅ Snapshot saved successfully."
        )


    # =====================================================
    # LOCATION
    # =====================================================

    st.divider()

    st.subheader(
        "📍 Emergency Location"
    )


    if st.button(
        "📍  CAPTURE MY LOCATION",
        use_container_width=True,
        key="safeher_location_button"
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

                location_data = {

                    "incident_id":
                        st.session_state.incident_id,

                    "timestamp":
                        now(),

                    "latitude":
                        location.get("latitude"),

                    "longitude":
                        location.get("longitude"),

                    "accuracy":
                        location.get("accuracy")
                }


                location_file = (
                    evidence_folder
                    / (
                        f"{st.session_state.incident_id}"
                        "_location.json"
                    )
                )


                location_file.write_text(
                    json.dumps(
                        location_data,
                        indent=2
                    ),
                    encoding="utf-8"
                )


                if not any(
                    item["type"] == "LOCATION"
                    for item in st.session_state.evidence
                ):

                    add_evidence(
                        "LOCATION",
                        location_file,
                        (
                            "GPS: "
                            + str(
                                location_data["latitude"]
                            )
                            + ", "
                            + str(
                                location_data["longitude"]
                            )
                        )
                    )


                st.success(
                    "✅ Location captured successfully."
                )


                col1, col2 = st.columns(2)


                with col1:

                    st.metric(
                        "📍 Latitude",
                        str(
                            location_data["latitude"]
                        )
                    )


                with col2:

                    st.metric(
                        "📍 Longitude",
                        str(
                            location_data["longitude"]
                        )
                    )


                if location_data.get("accuracy") is not None:

                    st.caption(
                        "🎯 Accuracy: "
                        + str(
                            location_data["accuracy"]
                        )
                        + " meters"
                    )


                try:

                    st.map(
                        {
                            "latitude": [
                                location_data["latitude"]
                            ],

                            "longitude": [
                                location_data["longitude"]
                            ]
                        }
                    )

                except Exception:

                    pass


            else:

                st.info(
                    "📍 Please allow location permission "
                    "in your browser and click "
                    "**CAPTURE MY LOCATION** again."
                )


        else:

            st.error(
                "Location component is unavailable. "
                "Make sure `streamlit-geolocation` "
                "is in requirements.txt."
            )


    # =====================================================
    # VIDEO
    # =====================================================

    st.divider()

    st.subheader(
        "🎥 Emergency Video Capture"
    )


    if VIDEO_AVAILABLE:

        st.info(
            "🎥 Press the START button below "
            "to activate the emergency camera."
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
                "safeher_emergency_video_"
                + str(
                    st.session_state.incident_id
                )
            ),

            mode=WebRtcMode.SENDRECV,

            rtc_configuration=rtc_configuration,

            # CAMERA ONLY
            # Microphone is intentionally disabled
            # to reduce permission problems.

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
            "Allow camera access when your browser "
            "requests permission."
        )


    else:

        st.error(
            "Video component unavailable. "
            "Make sure `streamlit-webrtc` and `av` "
            "are installed."
        )


# =========================================================
# EVIDENCE CAPTURED
# =========================================================

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
            <div class="evidence">

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


# =========================================================
# AI SAFETY CLASSIFICATION
# =========================================================

st.header(
    "🤖 AI Safety Classification"
)


description = st.text_area(

    "Describe the situation",

    placeholder=(
        "Example: Someone has been following me "
        "for the last 10 minutes..."
    ),

    key="safeher_safety_description"
)


if st.button(
    "🤖 Analyze Safety Situation",
    key="safeher_analyze_button"
):

    if description.strip():

        st.session_state.ai_result = classify(
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

st.header(
    "⚙️ Incident Controls"
)


if st.session_state.incident_active:

    if st.button(
        "🛑 End Incident",
        key="safeher_end_incident"
    ):

        end_incident()

        st.rerun()


if st.session_state.incident_id:

    manifest_file = (
        folder()
        / "evidence_manifest.json"
    )


    if manifest_file.exists():

        st.download_button(

            "⬇️ Download Incident Manifest",

            manifest_file.read_bytes(),

            file_name=(
                f"{st.session_state.incident_id}"
                "_manifest.json"
            ),

            mime="application/json",

            key="safeher_manifest_download"
        )


# =========================================================
# RESPONDER ACCESS
# =========================================================

st.divider()

st.header(
    "🛡️ Responder Access"
)


st.info(
    "Authorized responders can access the "
    "SafeHer emergency evidence dashboard."
)


st.code(
    "?mode=responder&key=safeher-demo"
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🌸 SafeHer AI — Personal safety technology demonstration."
)
