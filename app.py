from __future__ import annotations

import base64
from pathlib import Path
from uuid import uuid4

import streamlit as st

from src.alzheimers_speech.predict import predict_audio_with_fallback


st.set_page_config(page_title="Alzheimer Screening Studio", layout="wide", page_icon=":brain:")


def _resolve_background_style() -> str:
    image_path = Path(r"C:\Users\DELL\OneDrive\Pictures\background image of major.jpg")
    if image_path.exists():
        image_base64 = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return (
            "background-image: linear-gradient(rgba(14, 29, 44, 0.28), rgba(14, 29, 44, 0.44)), "
            f"url('data:image/jpeg;base64,{image_base64}');"
            "background-size: cover;"
            "background-position: center;"
            "background-repeat: no-repeat;"
            "background-attachment: fixed;"
        )
    return "background: linear-gradient(180deg, #f9fbfe 0%, var(--bg) 38%, #edf3fb 100%);"


_BACKGROUND_STYLE = _resolve_background_style()

style_block = """
    <style>
    :root {
        --navy: #19324a;
        --blue: #2f6fd4;
        --bg: #f5f8fc;
        --card: rgba(255, 255, 255, 0.95);
        --border: rgba(24, 48, 72, 0.10);
        --text: #17324a;
        --muted: #5f7185;
    }
    .stApp {
        __BACKGROUND_STYLE__
        color: var(--text);
    }
    .panel {
        border-radius: 24px;
        padding: 1.1rem 1.1rem 1rem;
        background: var(--card);
        border: 1px solid var(--border);
        box-shadow: 0 18px 40px rgba(27, 54, 89, 0.08);
        margin-bottom: 1rem;
    }
    .panel-title {
        font-size: 1rem;
        font-weight: 800;
        color: var(--navy);
        margin-bottom: 0.35rem;
    }
    .panel-note {
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.55;
        margin-bottom: 0.8rem;
    }
    .result-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.8rem;
    }
    .result-card {
        border-radius: 20px;
        padding: 1rem;
        background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(244,248,252,1));
        border: 1px solid rgba(21, 44, 68, 0.08);
    }
    .result-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.13em;
        color: #6d8095;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .result-value {
        font-size: 1.55rem;
        line-height: 1.1;
        font-weight: 850;
        color: var(--navy);
    }
    .result-subtext {
        margin-top: 0.35rem;
        color: #5b6d80;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    .status-ok { color: #0b7a4a; }
    .status-warn { color: #aa6b00; }
    .status-high { color: #b11d39; }
    .stButton > button {
        border-radius: 999px;
        padding: 0.75rem 1.2rem;
        border: none;
        background: linear-gradient(135deg, var(--blue), #245eb6);
        color: white;
        font-weight: 700;
        box-shadow: 0 12px 24px rgba(47, 111, 212, 0.22);
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 14px 28px rgba(47, 111, 212, 0.28);
    }
    .hero-title {
        font-size: clamp(2rem, 3.2vw, 2.9rem);
        font-weight: 900;
        letter-spacing: 0.02em;
        line-height: 1.08;
        margin: 0.2rem 0 0.15rem;
        color: #f7e679;
        text-shadow: 0 4px 22px rgba(17, 35, 58, 0.32);
    }
    .hero-subtitle {
        font-size: 1rem;
        font-weight: 700;
        color: #f4fbff;
        margin: 0 0 0.95rem;
        text-shadow: 0 2px 12px rgba(8, 19, 33, 0.56);
    }
    .mic-label {
        font-size: 0.96rem;
        font-weight: 800;
        margin: 0 0 0.55rem;
        color: #114162;
        background: linear-gradient(90deg, #ffb74a, #ffdf69);
        border: 1px solid rgba(219, 149, 46, 0.45);
        border-radius: 12px;
        padding: 0.45rem 0.7rem;
        display: inline-block;
    }
    </style>
    """.replace("__BACKGROUND_STYLE__", _BACKGROUND_STYLE)

st.markdown(style_block, unsafe_allow_html=True)

st.markdown("<div class='hero-title'>Alzheimer's Screening Studio</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='hero-subtitle'>Record speech live or upload an audio file, then review the screening summary and recommendations.</div>",
    unsafe_allow_html=True,
)

config_path = "configs/default.yaml"

if "active_audio_source" not in st.session_state:
    st.session_state.active_audio_source = None
if "prediction_rendered" not in st.session_state:
    st.session_state.prediction_rendered = False


def set_active_audio_source(source_name: str) -> None:
    st.session_state.active_audio_source = source_name
    st.session_state.prediction_rendered = False


left_col, right_col = st.columns([1.05, 0.95], gap="large")

with left_col:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Speech Input</div>
            <div class="panel-note">Use either option below. Upload an audio file or record live from your microphone.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload audio",
        type=["wav", "mp3", "m4a", "flac"],
        label_visibility="collapsed",
        key="audio_uploader",
        on_change=set_active_audio_source,
        args=("upload",),
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='panel'>", unsafe_allow_html=True)
    st.markdown("<div class='mic-label'>Record using microphone</div>", unsafe_allow_html=True)
    recorded_audio = st.audio_input(
        "Record using microphone",
        label_visibility="collapsed",
        key="audio_recorder",
        on_change=set_active_audio_source,
        args=("record",),
    )
    st.markdown("</div>", unsafe_allow_html=True)

    preview_source = st.session_state.active_audio_source
    if preview_source == "record" and recorded_audio is not None:
        st.audio(recorded_audio)
    elif preview_source == "upload" and uploaded_file is not None:
        st.audio(uploaded_file)
    elif recorded_audio is not None:
        st.audio(recorded_audio)
    elif uploaded_file is not None:
        st.audio(uploaded_file)

    predict_clicked = st.button("Analyze Recording", use_container_width=True)

with right_col:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Screening Result</div>
            <div class="panel-note">Results appear here after analysis.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    result_placeholder = st.empty()


def classify_risk(probability: float) -> str:
    if probability < 0.33:
        return "Low"
    if probability < 0.66:
        return "Moderate"
    return "High"


def clinical_recommendation(risk_level: str, suffering_status: str) -> list[str]:
    if suffering_status == "Yes" and risk_level == "High":
        return [
            "High concern: arrange an in-person neurological evaluation soon.",
            "Request formal cognitive screening such as MMSE or MoCA.",
            "Review medications, mood symptoms, sleep, and functional decline with a clinician.",
            "Include caregiver or family observations during consultation.",
        ]
    if suffering_status == "Yes" and risk_level == "Moderate":
        return [
            "Moderate concern: schedule clinician follow-up within 2 to 4 weeks.",
            "Perform structured cognitive and functional assessment.",
            "Track memory, language, and daily-activity changes week by week.",
        ]
    if suffering_status == "Yes" and risk_level == "Low":
        return [
            "Low model risk but symptoms are present: keep a clinician follow-up on schedule.",
            "Use a weekly symptom diary for memory, word-finding, and orientation changes.",
            "Repeat screening in 8 to 12 weeks or sooner if decline is noticed.",
        ]
    if suffering_status == "No" and risk_level == "High":
        return [
            "High model risk despite no current symptoms: book a clinical assessment promptly.",
            "Confirm with objective testing and a second speech sample in a quiet setting.",
            "Discuss reversible contributors such as hearing loss, sleep issues, and medications.",
        ]
    if suffering_status == "No" and risk_level == "Moderate":
        return [
            "Borderline finding: repeat screening in 4 to 8 weeks.",
            "Optimize sleep, hearing support, hydration, and stress control.",
            "Seek earlier clinical review if symptoms progress.",
        ]
    if suffering_status == "No" and risk_level == "Low":
        return [
            "Low immediate concern based on current sample and status.",
            "Maintain brain-healthy habits: physical activity, sleep regularity, and social engagement.",
            "Repeat routine screening in 6 to 12 months or earlier if concerns arise.",
        ]
    return [
        "Recommendation unavailable for this combination.",
        "Please repeat the assessment and review results with a clinician.",
    ]


if predict_clicked:
    if st.session_state.active_audio_source == "record":
        source_file = recorded_audio
    elif st.session_state.active_audio_source == "upload":
        source_file = uploaded_file
    else:
        source_file = recorded_audio if recorded_audio is not None else uploaded_file
    if source_file is None:
        result_placeholder.warning("Please upload or record an audio sample first.")
    else:
        try:
            suffix = Path(source_file.name).suffix if getattr(source_file, "name", None) else ".wav"
            if suffix == "":
                suffix = ".wav"
            temp_path = Path("data") / f"uploaded_sample_{uuid4().hex}{suffix}"
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_bytes(source_file.read())
            result = predict_audio_with_fallback(str(temp_path), config_path)
            probability = float(result["probability_alzheimer"])
            risk_level = classify_risk(probability)
            predicted_class = int(result.get("predicted_class", 0))
            suffering_status = "Yes" if predicted_class == 1 else "No"
            recommendation_points = clinical_recommendation(risk_level, suffering_status)
            recommendation_html = "".join(f"<li>{point}</li>" for point in recommendation_points)
            pause_count = int(result.get("pause_count", 0))
            speech_ratio = float(result.get("speech_ratio", 0.0))
            dominant_frequency_hz = float(result.get("dominant_frequency_hz", 0.0))
            mean_pitch_hz = float(result.get("mean_pitch_hz", 0.0))
            pitch_std_hz = float(result.get("pitch_std_hz", 0.0))

            status_class = "status-high" if risk_level == "High" else "status-warn" if risk_level == "Moderate" else "status-ok"

            result_placeholder.markdown(
                f"""
                <div class="result-grid">
                    <div class="result-card">
                        <div class="result-label">Risk Level</div>
                        <div class="result-value {status_class}">{risk_level}</div>
                        <div class="result-subtext">Screening category based on the detected speech patterns.</div>
                    </div>
                    <div class="result-card">
                        <div class="result-label">Suffering with Alzheimer's</div>
                        <div class="result-value {status_class}">{suffering_status}</div>
                        <div class="result-subtext">Binary screening result for quick review.</div>
                    </div>
                </div>
                <div class="result-card" style="margin-top:0.8rem;">
                    <div class="result-label">Clinical Recommendation</div>
                    <ul class="result-subtext" style="margin-top:0;padding-left:1.2rem;">{recommendation_html}</ul>
                </div>
                <div class="result-card" style="margin-top:0.8rem;">
                    <div class="result-label">Audio Diagnostics</div>
                    <div class="result-subtext">
                        Pause count (&gt;=0.2s): <strong>{pause_count}</strong><br/>
                        Speech ratio: <strong>{speech_ratio:.3f}</strong><br/>
                        Dominant frequency (Hz): <strong>{dominant_frequency_hz:.2f}</strong><br/>
                        Mean pitch (Hz): <strong>{mean_pitch_hz:.2f}</strong><br/>
                        Pitch std (Hz): <strong>{pitch_std_hz:.2f}</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.session_state.prediction_rendered = True
        except Exception as exc:
            result_placeholder.error(f"Prediction failed: {exc}")

