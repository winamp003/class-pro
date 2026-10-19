"""SOLAR SITE LAB: 학생 참여형 태양광 입지 선정 디지털 학습지."""

import html
import math
from datetime import datetime
from io import StringIO
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# 모든 수치는 수업용 가상 데이터이며 실제 지역이나 인허가 기준이 아닙니다.
SITES = ["A 내륙 평야", "B 구릉지", "C 해안 저지", "D 산업단지 인접"]
# 항목 키: (화면 표시 이름, 단위, 큰 값이 유리한지, 기본 가중치)
CRITERIA = {
    "solar": ("일사량", "kWh/㎡/일", True, 30),
    "cost": ("토지 비용", "억원", False, 20),
    "slope": ("경사도", "°", False, 15),
    "grid": ("전력망 연결 거리", "km", False, 20),
    "environment": ("환경 수용성", "점", True, 15),
}
DATA = pd.DataFrame({
    "solar": [4.3, 4.7, 4.0, 4.4],
    "cost": [6, 5, 4, 8],
    "slope": [3, 14, 2, 5],
    "grid": [3, 9, 6, 1],
    "environment": [4, 2, 5, 3],
}, index=pd.Index(SITES, name="후보 지역"))
PRESETS = {
    "균형 평가": dict(zip(CRITERIA, [30, 20, 15, 20, 15])),
    "발전량 중심": dict(zip(CRITERIA, [60, 10, 10, 10, 10])),
    "환경 중심": dict(zip(CRITERIA, [10, 20, 15, 10, 45])),
}
MISSIONS = ["사전 예상", "핵심 개념", "지역 데이터", "평가 기준", "시뮬레이션", "최종 선정", "학습 성찰"]
TITLES = [
    "먼저 예상해 보자!", "태양광 입지 선정 전문가가 되어 보자!",
    "후보 지역의 데이터를 분석하라!", "나만의 평가 기준을 설계하라!",
    "평가 기준을 바꾸면 결과도 달라질까?", "최적의 태양광 발전단지를 선정하라!",
    "처음의 생각과 지금의 생각을 비교하라!",
]
MISSION_GUIDES = [
    "데이터를 보기 전의 생각을 기록하세요. 마지막 미션에서 처음의 판단과 비교합니다.",
    "다섯 가지 입지 조건을 학습하고, 각 값이 커질 때 유리한지 판단해 보세요.",
    "비교 지표를 바꾸며 네 후보지의 강점과 약점을 찾고, 바로 아래 질문에 답하세요.",
    "중요도를 직접 설계하세요. 합계 100%인 가중치의 점수와 순위가 즉시 표시됩니다.",
    "가중치와 사업 조건을 바꿔 보세요. 같은 자료에서도 1위가 달라지는 이유를 찾아봅니다.",
    "최종 지역을 선택하고 데이터에 근거한 두 가지 이유와 문제 해결 방안을 작성하세요.",
    "처음과 마지막의 판단을 비교하고, 활동 중 작성한 내용을 나의 탐구 보고서로 저장하세요.",
]
ICONS = {"solar": "☀️", "cost": "🪙", "slope": "⛰️", "grid": "⚡", "environment": "🌿"}
PALETTES = {
    "light": {
        "bg": "#F4F7F6", "surface": "#FFFFFF", "sidebar": "#EBF1EE", "input": "#F8FAF9",
        "text": "#243442", "muted": "#596B76", "border": "#D6E2DB", "green": "#18794E",
        "soft": "#E7F3EC", "yellow": "#F3B63F", "button_text": "#FFFFFF", "grid": "#E4ECE7",
    },
    "dark": {
        "bg": "#0E1816", "surface": "#172622", "sidebar": "#12201C", "input": "#20332C",
        "text": "#EAF2EE", "muted": "#B2C4BA", "border": "#3C564A", "green": "#73DDA6",
        "soft": "#203E2E", "yellow": "#F7C862", "button_text": "#10251A", "grid": "#30473D",
    },
}
INPUT_HINTS = {
    "student_id": "예: 10101", "student_name": "예: 김태양",
    "q2": "이 조건이 발전량, 비용 또는 주변 환경과 어떤 관련이 있는지 적어 보세요.",
    "q3_reason": "지금 생각하는 이유를 자유롭게 적어 보세요. 마지막에 다시 살펴봅니다.",
    "q5": "토지 비용, 지형, 전력망, 환경 중 다른 조건과 연결해 설명해 보세요.",
    "q10": "서로 다른 지표의 값이 반드시 함께 좋아지는지 생각해 보세요.",
    "q11_reason": "유리한 조건과 실제 수치를 한 가지 이상 연결해 보세요.",
    "q13": "어떤 목표를 중요하게 생각했는지 자신의 평가 기준을 설명해 보세요.",
    "q15": "1위가 된 지역의 강점과 해당 항목의 가중치를 연결해 설명하세요.",
    "q19_1": "선택한 지역의 수치를 다른 지역과 비교해 첫 번째 근거를 작성하세요.",
    "q19_2": "첫 번째 근거와 다른 입지 조건을 활용해 두 번째 근거를 작성하세요.",
    "q20_problem": "선택한 지역이 다른 후보보다 불리한 조건을 찾아보세요.",
    "q20_solution": "위 문제에 대응할 수 있는 조사, 설계 또는 사업 계획을 제안해 보세요.",
    "q22": "처음 예상과 달라진 점 또는 판단을 뒷받침하게 된 데이터를 적어 보세요.",
    "q23": "이번 탐구에서 배운 점을 자신의 말로 정리해 보세요.",
}
CONCEPTS = {
    "solar": "일정 면적에 도달하는 태양에너지의 양입니다. 다른 조건이 같다면 일사량이 많을수록 발전에 유리합니다.",
    "cost": "발전단지를 위한 토지 확보 비용입니다. 다른 조건이 같다면 토지 비용이 낮을수록 경제적으로 유리합니다.",
    "slope": "지면이 기울어진 정도입니다. 경사가 크면 토목공사와 설비 설치에 추가 비용이 발생할 수 있습니다.",
    "grid": "생산한 전기를 송전·배전 계통에 연결하기 위한 거리입니다. 거리가 길면 연결 공사비가 커질 수 있습니다.",
    "environment": "자연환경과 주변 지역에 미치는 영향을 고려한 교육용 지표입니다. 1~5점 중 5점이 가장 유리합니다.",
}
PHOTO_CAPTIONS = {
    "solar_farm": "햇빛을 전기로 바꾸는 태양광 발전단지",
    "inland_plain": "넓고 평탄한 내륙 부지",
    "hillside": "공사 조건을 살펴봐야 하는 구릉지",
    "coastal_land": "주변 자연환경을 함께 고려할 해안 저지",
    "industrial_land": "건물과 전력 설비가 가까운 산업단지 주변",
    "power_grid": "만들어진 전기를 전달하는 전력망",
}
CONCEPT_PHOTOS = {"solar": "solar_farm", "cost": "inland_plain", "slope": "hillside",
                  "grid": "power_grid", "environment": "coastal_land"}
CANDIDATE_PHOTOS = ["inland_plain", "hillside", "coastal_land", "industrial_land"]
THEORY_TITLES = ["햇빛이 우리 교실의 전기가 되기까지", "좋은 땅 찾기는 가게 자리 찾기와 닮았어요",
                "전기의 길과 자연의 자리를 함께 살펴요", "가중치는 심사위원의 별 스티커예요"]
QUESTIONS = {
    "q1": "Q1. 가장 중요하다고 생각하는 입지 조건은 무엇인가요?",
    "q2": "Q2. 위 조건을 선택한 이유는 무엇인가요?",
    "q3": "Q3. 일사량이 가장 높은 지역이 항상 유리할까요?",
    "q3_reason": "Q3. 선택 이유",
    "initial_site": "분석 전 최초 예상 지역",
    **{f"q4_{k}": f"Q4. {v[0]} 증가의 유불리" for k, v in CRITERIA.items()},
    "q5": "Q5. 일사량이 높아도 발전단지 건설에 불리할 수 있는 이유는 무엇인가요?",
    "q6": "Q6. 일사량이 가장 높은 지역은 어디인가요?",
    "q7": "Q7. 토지 비용이 가장 저렴한 지역은 어디인가요?",
    "q8": "Q8. 경사도가 가장 낮은 지역은 어디인가요?",
    "q9": "Q9. 전력망 연결 거리가 가장 짧은 지역은 어디인가요?",
    "q10": "Q10. 일사량 1위와 전력망 연결 거리가 가장 짧은 지역이 서로 다른 이유는 무엇일까요?",
    "q11": "Q11. 자료 확인 후 가장 적합하다고 생각하는 지역은 어디인가요?",
    "q11_reason": "Q11. 선정 이유",
    "q12": "Q12. 가장 높은 가중치를 설정한 항목은 무엇인가요?",
    "q13": "Q13. 해당 항목을 가장 중요하게 판단한 이유는 무엇인가요?",
    "q15": "Q15. 평가 기준을 변경하면 결과가 달라지는 이유는 무엇인가요?",
    "q16": "Q16. 종합점수 1위라면 어떤 상황에서도 발전단지를 건설해도 될까요?",
    "q16_reason": "Q16. 선택 이유",
    "q17": "Q17. 최종 선정 지역",
    "q19_1": "Q19. 객관적인 선정 근거 1",
    "q19_2": "Q19. 객관적인 선정 근거 2",
    "q20_problem": "Q20. 선정 지역의 단점 또는 예상 문제점",
    "q20_solution": "Q20. 해결 방안",
    "q21": "Q21. 최초 예상 지역과 최종 선정 지역이 같나요?",
    "q22": "Q22. 선택이 달라지거나 기존 생각이 더 확고해진 이유는 무엇인가요?",
    "q23": "Q23. 활동을 통해 알게 된 입지 선정의 핵심 조건은 무엇인가요?",
}


def valid_weights(weights):
    """합계 100%인 비음수 가중치만 허용하고 자동 보정하지 않습니다."""
    return (
        set(weights) == set(CRITERIA)
        and all(isinstance(v, (int, float)) and math.isfinite(v) and 0 <= v <= 100
                for v in weights.values())
        and math.isclose(sum(weights.values()), 100, abs_tol=1e-9)
    )


def normalize_data(data):
    """최소–최대 정규화. 최신 학습 지침에 따라 동일값은 모두 100점."""
    normalized = pd.DataFrame(index=data.index)
    for key, (_, _, higher, _) in CRITERIA.items():
        values = data[key].astype(float)
        low, high = values.min(), values.max()
        if high == low:
            normalized[key] = 100.0
        elif higher:
            normalized[key] = (values - low) / (high - low) * 100
        else:
            normalized[key] = (high - values) / (high - low) * 100
    return normalized


def evaluate_sites(weights, max_slope=None, data=None):
    """원래 후보 전체로 정규화한 뒤 제한을 적용합니다. 동점은 공동 순위."""
    if not valid_weights(weights):
        raise ValueError("가중치 합계는 100%여야 합니다.")
    data = DATA if data is None else data
    contributions = normalize_data(data).mul(pd.Series(weights)) / 100
    result = contributions.rename(columns={k: f"{v[0]} 반영점수" for k, v in CRITERIA.items()})
    result["종합점수"] = contributions.sum(axis=1)
    result["평가 대상"] = True if max_slope is None else data["slope"] <= max_slope
    result["제외 사유"] = ""
    if max_slope is not None:
        excluded = ~result["평가 대상"]
        result.loc[excluded, "제외 사유"] = data.loc[excluded, "slope"].map(
            lambda value: f"경사도 {value:g}° > 수업용 상한 {max_slope:g}°"
        )
    result["순위"] = result["종합점수"].where(result["평가 대상"]).round(10).rank(
        ascending=False, method="min"
    ).astype("Int64")
    return result.sort_values(["평가 대상", "종합점수"], ascending=[False, False], kind="stable")


def leaders(result):
    return result.index[result["순위"].eq(1).fillna(False)].tolist()


def weight_table(weights):
    return pd.DataFrame({
        "평가항목": [v[0] for v in CRITERIA.values()],
        "가중치(%)": [weights[k] for k in CRITERIA],
    })


def display_data():
    return DATA.rename(columns={k: f"{v[0]} ({v[1]})" for k, v in CRITERIA.items()})


# 화면에서 사라진 위젯의 상태는 Streamlit이 정리합니다.
# 원본 답변은 별도 딕셔너리에 저장해 미션 이동 후에도 유지합니다.
def save_answer(key):
    st.session_state.answers[key] = st.session_state[f"_answer_{key}"]


def text_answer(key, label=None, short=False, help=None):
    widget_key = f"_answer_{key}"
    st.session_state[widget_key] = st.session_state.answers.get(key, "")
    widget = st.text_input if short else st.text_area
    with st.container(border=True, key=f"response_{key}"):
        return widget(label or QUESTIONS[key], key=widget_key,
                      on_change=save_answer, args=(key,), help=help,
                      placeholder=INPUT_HINTS.get(key, "자료를 바탕으로 자신의 생각을 1~2문장으로 작성하세요."))


def choice_answer(key, options, label=None, horizontal=False):
    widget_key = f"_answer_{key}"
    st.session_state[widget_key] = st.session_state.answers.get(key)
    with st.container(border=True, key=f"response_{key}"):
        return st.radio(label or QUESTIONS[key], options, index=None, key=widget_key,
                        horizontal=horizontal, on_change=save_answer, args=(key,))


def save_weight(key):
    st.session_state.weights[key] = st.session_state[f"_weight_{key}"]
    st.session_state.pop("weight_notice", None)


def apply_preset(name):
    st.session_state.weights = PRESETS[name].copy()
    st.session_state.pop("weight_notice", None)


def convert_weights(weights):
    """비율을 정수 %로 환산하고 잔여값을 마지막 항목에 반영합니다."""
    total = sum(weights.values())
    if total == 0:
        return None
    scaled = [weights[k] * 100 / total for k in CRITERIA]
    values = [round(v) for v in scaled[:-1]]
    # 앞 네 항목의 반올림 합이 100을 넘으면 마지막 값이 음수가 되지 않게 조정합니다.
    while sum(values) > 100:
        index = max(range(len(values)), key=lambda i: values[i] - scaled[i])
        values[index] -= 1
    values.append(100 - sum(values))
    return dict(zip(CRITERIA, values))


def auto_convert_weights():
    converted = convert_weights(st.session_state.weights)
    if converted is None:
        st.session_state.weight_notice = "모든 항목이 0%입니다. 한 항목 이상에 값을 입력한 뒤 환산해 주세요."
    else:
        st.session_state.weights = converted
        st.session_state.weight_notice = "비율을 기준으로 합계를 100%로 환산했습니다. 반올림 잔여값은 마지막 항목에 반영했습니다."


def save_setting(key):
    st.session_state.settings[key] = st.session_state[f"_setting_{key}"]


def go_to_mission(index):
    st.session_state.mission = index


def scroll_to_top_on_navigation(view):
    """화면이 바뀔 때만 스크롤합니다. 답변 입력·슬라이더 조작 때는 위치를 유지합니다."""
    if st.session_state.get("last_scroll_view") == view:
        return
    st.session_state.last_scroll_view = view
    # 매번 다른 스크립트로 렌더링하여 같은 화면을 다시 방문해도 실행합니다.
    request = st.session_state.get("scroll_request", 0) + 1
    st.session_state.scroll_request = request
    st.html(
        f'<script data-scroll-request="{request}">' + """
        (() => {
            const resetScroll = () => {
                // Streamlit 본문과 모바일 브라우저의 스크롤 영역을 함께 처리합니다.
                const targets = new Set([
                    document.querySelector('[data-testid="stMain"]'),
                    document.querySelector('[data-testid="stAppViewContainer"]'),
                    document.scrollingElement,
                ]);
                for (const target of targets) {
                    if (target) target.scrollTo({top: 0, left: 0, behavior: "instant"});
                }
                window.scrollTo({top: 0, left: 0, behavior: "instant"});
            };
            // 새 화면의 렌더링과 스크롤 위치 복원이 끝난 뒤 위로 이동합니다.
            requestAnimationFrame(() => requestAnimationFrame(resetScroll));
            setTimeout(resetScroll, 150);
        })();
        </script>
        """,
        unsafe_allow_javascript=True,
    )


def answered(*keys):
    return all(str(st.session_state.answers.get(k) or "").strip() for k in keys)


def completion_status(weights, max_slope):
    answers = st.session_state.answers
    final_site = answers.get("q17")
    eligible = final_site in SITES and (max_slope is None or DATA.loc[final_site, "slope"] <= max_slope)
    comparison = "같다" if answers.get("initial_site") == final_site else "다르다"
    highest = [CRITERIA[k][0] for k, v in weights.items() if v == max(weights.values())]
    return [
        answered("q1", "q2", "q3", "q3_reason", "initial_site"),
        answered(*(f"q4_{k}" for k in CRITERIA), "q5"),
        answered("q6", "q7", "q8", "q9", "q10", "q11", "q11_reason"),
        valid_weights(weights) and answered("q12", "q13") and answers.get("q12") in highest,
        answered("q15", "q16", "q16_reason"),
        valid_weights(weights) and eligible and answered("q17", "q19_1", "q19_2", "q20_problem", "q20_solution"),
        answered("initial_site", "q17", "q21", "q22", "q23") and answers.get("q21") == comparison,
    ]


def current_palette():
    preference = st.session_state.get("appearance", "자동")
    native_theme = st.context.theme.type
    mode = {"라이트": "light", "다크": "dark"}.get(preference, native_theme or "light")
    return PALETTES[mode]


def apply_design():
    """화면과 입력 요소에 같은 팔레트를 사용합니다. 개발 환경 설정은 바꾸지 않습니다."""
    palette = current_palette()
    variables = ";".join(f"--lab-{name.replace('_', '-')}: {value}" for name, value in palette.items())
    scheme = "dark" if palette is PALETTES["dark"] else "light"
    st.markdown("<style>:root{" + variables + f";color-scheme:{scheme}" + "}" + """
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
        background: var(--lab-bg); color: var(--lab-text);
        font-family: 'Pretendard', 'Noto Sans KR', 'Malgun Gothic', sans-serif;
    }
    .block-container { max-width: 1220px; padding-bottom: 3rem; }
    [data-testid="stMain"] .block-container {
        padding-top: calc(5.5rem + env(safe-area-inset-top, 0px));
    }
    [data-testid="stMain"] { scroll-padding-top: 6rem; }
    [data-testid="stHeader"] { background: var(--lab-bg); color: var(--lab-text); }
    [data-testid="stHeader"] button, [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button { color: var(--lab-text); }
    [data-testid="stSidebar"] { background: var(--lab-sidebar); border-right: 1px solid var(--lab-border); }
    .stApp h1, .stApp h2, .stApp h3, .stApp h4,
    [data-testid="stMarkdownContainer"], [data-testid="stText"],
    [data-testid="stWidgetLabel"], [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: var(--lab-text);
    }
    .stApp h1 { font-size: clamp(26px, 3.2vw, 32px); line-height: 1.35; letter-spacing: -.04em; }
    .stApp h2 { font-size: 26px; letter-spacing: -.035em; }
    .stApp h3 { font-size: 19px; }
    [data-testid="stMarkdownContainer"] p, [data-testid="stWidgetLabel"] p { font-size: 15px; line-height: 1.75; }
    [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p {
        color: var(--lab-muted); font-size: 13px; line-height: 1.7;
    }
    [data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
    [data-testid="stSidebar"] [class*="st-key-response_"] { background: transparent; }
    .st-key-mission [role="radiogroup"] { gap: 6px; }
    .st-key-mission label { padding: 10px 12px; border: 1px solid transparent; border-radius: 10px; }
    .st-key-mission label:has(input:checked) { background: var(--lab-soft); border-color: var(--lab-green); }
    .st-key-mission label:has(input:checked) p { color: var(--lab-green); font-weight: 700; }
    .st-key-mission label:hover { background: var(--lab-soft); }
    [data-testid="stMetric"], [class*="st-key-response_"], [class*="st-key-card_"] {
        background: var(--lab-surface); border-radius: 14px;
    }
    [data-testid="stMetric"] { padding: 19px; border: 1px solid var(--lab-border); min-width: 0; }
    [data-testid="stMetricValue"] { font-size: clamp(22px, 2.8vw, 30px); }
    [data-testid="stMetricDelta"] { color: var(--lab-muted); }
    [data-testid="stVerticalBlockBorderWrapper"] > div,
    [data-testid="stVerticalBlock"][style*="border:"] { border-color: var(--lab-border) !important; }
    [data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        color: var(--lab-text) !important; background: var(--lab-input) !important;
        caret-color: var(--lab-green); border-radius: 9px;
    }
    [data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"],
    [data-baseweb="select"] > div {
        color: var(--lab-text) !important; background: var(--lab-input) !important;
        border-color: var(--lab-border) !important;
    }
    input::placeholder, textarea::placeholder { color: var(--lab-muted) !important; opacity: .85; }
    [data-baseweb="popover"] [role="listbox"], [data-baseweb="popover"] [role="option"] {
        background: var(--lab-surface); color: var(--lab-text);
    }
    [data-baseweb="popover"] [role="option"]:hover { background: var(--lab-soft); }
    [data-baseweb="select"] svg { fill: var(--lab-muted); }
    [data-baseweb="select"] span, [data-baseweb="select"] input { color: var(--lab-text) !important; }
    [data-testid="stBaseButton-secondary"], [data-testid="stBaseButton-secondaryFormSubmit"],
    [data-testid="stDownloadButton"] button {
        background: var(--lab-surface); color: var(--lab-text); border: 1px solid var(--lab-border);
        border-radius: 9px; min-height: 42px;
    }
    [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-primaryFormSubmit"] {
        background: var(--lab-green); color: var(--lab-button-text); border-color: var(--lab-green);
        border-radius: 9px; min-height: 44px;
    }
    [data-testid="stBaseButton-primary"] p, [data-testid="stBaseButton-primaryFormSubmit"] p {
        color: var(--lab-button-text);
    }
    .stButton button:disabled { opacity: .45; }
    .stButton button:hover:not(:disabled), [data-testid="stDownloadButton"] button:hover {
        border-color: var(--lab-green); filter: brightness(1.04);
    }
    [data-testid="stProgress"] [role="progressbar"] > div > div { background-color: var(--lab-green); }
    [data-baseweb="slider"] [role="slider"] { background-color: var(--lab-green); }
    [data-testid="stSlider"] [data-testid="stMarkdownContainer"] { color: var(--lab-text); }
    [data-testid="stAlert"] { background: var(--lab-soft); color: var(--lab-text); border: 1px solid var(--lab-border); }
    [data-testid="stAlert"] p { color: var(--lab-text); }
    [data-testid="stExpander"] { background: var(--lab-surface); border-color: var(--lab-border); border-radius: 12px; }
    [data-testid="stExpander"] details, [data-testid="stExpander"] summary {
        background: var(--lab-surface); color: var(--lab-text); border-radius: 12px;
    }
    [data-baseweb="tab-list"] { gap: 12px; border-bottom-color: var(--lab-border); }
    [data-baseweb="tab"] { color: var(--lab-muted); }
    [data-baseweb="tab"][aria-selected="true"] { color: var(--lab-green); }
    [data-baseweb="tab-highlight"] { background-color: var(--lab-green); }
    [data-testid="stTable"] { color: var(--lab-text); background: var(--lab-surface); }
    [data-testid="stTable"] th, [data-testid="stTable"] td {
        color: var(--lab-text); background: var(--lab-surface); border-color: var(--lab-border);
    }
    .lab-brand { display: flex; align-items: center; gap: 10px; margin-bottom: 18px; }
    .lab-sun { background: var(--lab-yellow); color: #243442; border-radius: 12px; padding: 9px 12px; font-size: 25px; }
    .lab-wordmark { color: var(--lab-text); font-size: 19px; font-weight: 800; letter-spacing: .04em; }
    .lab-wordmark small { display: block; color: var(--lab-muted); font-size: 11px; font-weight: 500; margin-top: 4px; letter-spacing: 0; }
    .lab-topline { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; margin-bottom: 14px; }
    .lab-topline strong { color: var(--lab-text); font-size: 16px; letter-spacing: .04em; }
    .lab-topline small { display: block; color: var(--lab-muted); font-size: 13px; margin-top: 3px; }
    .lab-badge { display: inline-block; background: var(--lab-soft); color: var(--lab-green); border: 1px solid var(--lab-border);
        padding: 6px 12px; border-radius: 99px; font-size: 12px; font-weight: 700; }
    .lab-kicker { color: var(--lab-green); font-size: 12px; font-weight: 800; letter-spacing: .12em; margin: 26px 0 8px; }
    .lab-guide { color: var(--lab-muted); line-height: 1.8; margin: -4px 0 24px; font-size: 15px; }
    .lab-section { display: flex; align-items: center; gap: 9px; color: var(--lab-text); font-size: 19px; font-weight: 750; margin: 24px 0 14px; }
    .lab-section span { color: var(--lab-green); background: var(--lab-soft); border-radius: 7px; padding: 4px 8px; font-size: 12px; }
    .lab-hero { border: 1px solid var(--lab-border); background: var(--lab-surface); border-radius: 16px; padding: 24px; }
    .lab-hero svg { width: 100%; max-height: 230px; }
    [data-testid="stImage"] img { border-radius: 14px; max-height: 360px; object-fit: cover; }
    .lab-flow { display: flex; gap: 10px; align-items: stretch; flex-wrap: wrap; margin: 20px 0; }
    .lab-flow-item { flex: 1 1 150px; background: var(--lab-soft); border: 1px solid var(--lab-border);
        border-radius: 12px; padding: 16px; color: var(--lab-text); text-align: center; line-height: 1.7; }
    .lab-flow-item strong { display: block; color: var(--lab-green); font-size: 16px; }
    .lab-story { background: var(--lab-surface); border-left: 4px solid var(--lab-yellow);
        border-radius: 0 12px 12px 0; padding: 18px 22px; color: var(--lab-text); line-height: 1.9; margin: 18px 0; }
    .lab-note { border-left: 3px solid var(--lab-yellow); background: var(--lab-soft); border-radius: 0 9px 9px 0;
        color: var(--lab-muted); padding: 12px 16px; font-size: 13px; line-height: 1.8; margin: 18px 0; }
    a { color: var(--lab-green); }
    hr { border-color: var(--lab-border); }
    @media (max-width: 680px) {
        .block-container { padding: 1.2rem 1rem 2rem; }
        [data-testid="stMain"] .block-container {
            padding-top: calc(5.25rem + env(safe-area-inset-top, 0px));
        }
        [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 12px; }
        [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { width: 100% !important; flex: 1 1 100% !important; min-width: 0 !important; }
        .lab-hero { padding: 18px; }
        .lab-topline small { max-width: 270px; }
        [data-testid="stImage"] img { max-height: 260px; }
    }
    </style>
    """, unsafe_allow_html=True)


def section_heading(number, title):
    st.markdown(f'<div class="lab-section"><span>{number}</span>{html.escape(title)}</div>', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def photo_bytes(key):
    return (Path(__file__).parent / "assets" / f"{key}.webp").read_bytes()


def show_photo(key):
    st.image(photo_bytes(key), width="stretch", output_format="JPEG",
             caption=PHOTO_CAPTIONS[key] + " · AI 생성 학습용 이미지")


def candidate_gallery(show_values=False):
    for start in range(0, len(SITES), 2):
        for column, index in zip(st.columns(2), range(start, min(start + 2, len(SITES)))):
            with column:
                with st.container(border=True, key=f"card_candidate_photo_{index}"):
                    st.subheader(SITES[index])
                    show_photo(CANDIDATE_PHOTOS[index])
                    if show_values:
                        row = DATA.loc[SITES[index]]
                        st.caption(f"일사량 {row['solar']:.1f} kWh/㎡/일 · 경사도 {row['slope']:g}° · "
                                   f"전력망 거리 {row['grid']:g} km")
    st.caption("사진은 후보지 유형을 이해하기 위한 AI 생성 예시입니다. 평가에는 아래 표의 가상 데이터를 사용합니다.")


def open_theory():
    st.session_state.theory_open = True
    st.session_state.theory_step = 0


def finish_theory():
    st.session_state.theory_completed = True
    st.session_state.theory_open = False


def change_theory_step(step):
    st.session_state.theory_step = step


def save_theory_share():
    st.session_state.theory_share = st.session_state._theory_share


def show_theory():
    """본 학습지 전에 사진·비유·가벼운 조작으로 만나는 네 장면의 준비 학습."""
    step = st.session_state.theory_step
    st.markdown('<div class="lab-kicker">CONCEPT LAB · 미션 전 준비 운동</div>', unsafe_allow_html=True)
    st.header(THEORY_TITLES[step])
    st.caption("약 3~5분 · 사진과 작은 실험으로 개념을 익혀요. 이 활동은 미션 답변이나 평가 가중치를 바꾸지 않습니다.")
    st.progress((step + 1) / 4, text=f"이론 탐험 {step + 1}/4 · {['햇빛과 전기', '부지와 비용', '전력망과 환경', '가중치 맛보기'][step]}")

    if step == 0:
        show_photo("solar_farm")
        st.markdown('<div class="lab-story">학교의 조명과 컴퓨터가 햇빛으로 움직인다면 어떨까요? '
                    '태양광 모듈 속 <strong>태양전지</strong>가 빛에너지를 전기에너지로 바꿔 줍니다. '
                    '여러 모듈이 모이면 사진처럼 하나의 발전단지가 됩니다.</div>', unsafe_allow_html=True)
        st.markdown('<div class="lab-flow">'
                    '<div class="lab-flow-item"><strong>☀️ 햇빛</strong>발전에 사용할 에너지</div>'
                    '<div class="lab-flow-item"><strong>▦ 태양광 모듈</strong>직류 전기 만들기</div>'
                    '<div class="lab-flow-item"><strong>⚙️ 인버터</strong>직류를 교류로 바꾸기</div>'
                    '<div class="lab-flow-item"><strong>⚡ 전력망</strong>전기를 필요한 곳으로 전달</div>'
                    '</div>', unsafe_allow_html=True)
        st.info("오늘의 핵심 질문: 햇빛이 가장 많은 곳에 지으면 언제나 최고의 발전단지가 될까요?")
        with st.expander("낯선 말도 가볍게 · kW와 kWh"):
            st.write("kW는 설비가 전기를 만들어 낼 수 있는 능력을 나타내고, kWh는 일정 시간 동안 만든 전기에너지의 양을 나타냅니다. "
                     "이 프로젝트의 1MW는 1,000kW입니다. 실제 발전량은 햇빛과 설비 상태 등에 따라 달라집니다.")

    elif step == 1:
        st.markdown('<div class="lab-story">떡볶이 가게를 연다고 상상해 봐요. 손님이 많은 자리도 좋지만 '
                    '<strong>임대료와 배달 동선</strong>도 살펴봐야겠죠? 발전단지도 햇빛과 함께 '
                    '<strong>땅값과 공사하기 쉬운 정도</strong>를 비교합니다.</div>', unsafe_allow_html=True)
        left, right = st.columns(2)
        with left:
            show_photo("inland_plain")
            st.write("**넓고 평탄한 땅** · 설비를 배치하고 공사 차량이 드나드는 조건을 살펴볼 수 있어요.")
        with right:
            show_photo("hillside")
            st.write("**경사진 땅** · 부지 조성과 설비 설치에 어떤 추가 작업이 필요할지 생각해 봐요.")
        for title, body in [
            ("☀️ 일사량 = 햇빛 에너지의 양", "다른 조건이 같다면 더 많은 일사에너지를 이용할수록 발전에 유리해요."),
            ("🪙 토지 비용 = 자리를 마련하는 비용", "같은 사업 예산이라면 땅을 확보하는 비용도 중요해요."),
            ("⛰️ 경사도 = 땅이 기울어진 정도", "다른 조건이 같다면 완만한 땅은 토목공사와 설치 부담을 줄이는 데 유리해요."),
        ]:
            with st.container(border=True):
                st.subheader(title)
                st.write(body)
        st.caption("사진의 겉모습만으로 사업성을 결정할 수는 없어요. 잠시 뒤에는 실제 비교에 사용할 가상 수치를 확인합니다.")

    elif step == 2:
        show_photo("power_grid")
        st.markdown('<div class="lab-story">발전단지는 전기를 만드는 주방, 전력망은 전기를 배달하는 길이라고 '
                    '생각해 봐요. 연결 지점까지 멀면 <strong>전선을 잇는 공사와 비용</strong>도 함께 검토해야 합니다.</div>',
                    unsafe_allow_html=True)
        left, right = st.columns(2)
        with left:
            show_photo("industrial_land")
            st.write("**⚡ 전력망 접근성** · 어디로 연결할 수 있는지와 연결 지점까지의 거리를 함께 살펴봐요.")
        with right:
            show_photo("coastal_land")
            st.write("**🌿 환경 수용성** · 주변 생태와 지역에 어떤 영향을 주는지 생각해 봐요.")
        st.info("이 학습지의 환경 수용성은 1~5점의 교육용 값입니다. 점수가 높을수록 유리하다고 가정해요. "
                "다섯 조건을 함께 비교하면 더 설득력 있는 선택을 할 수 있어요.")

    else:
        st.markdown('<div class="lab-story">심사위원에게 <strong>별 스티커 100개</strong>가 있다고 상상해 봐요. '
                    '중요하다고 생각하는 조건에 스티커를 더 붙이는 것이 <strong>가중치</strong>예요. '
                    '일사량에 30개를 붙이면 가중치는 30%가 됩니다.</div>', unsafe_allow_html=True)
        st.session_state._theory_share = st.session_state.theory_share
        share = st.slider("햇빛에 별 스티커를 몇 개 붙여 볼까요?", 10, 90, step=10, format="%d개",
                          key="_theory_share", on_change=save_theory_share)
        st.caption("남은 스티커는 나머지 네 조건에 똑같이 나눕니다. 연습용 슬라이더이며 미션의 평가 기준에는 영향을 주지 않습니다.")
        palette = current_palette()
        figure = go.Figure(go.Pie(
            labels=[v[0] for v in CRITERIA.values()], values=[share] + [(100 - share) / 4] * 4,
            hole=.62, sort=False, textinfo="none",
            marker_colors=[palette["yellow"], palette["green"], "#52B8AF", "#6FADDF", "#B095DA"],
            hovertemplate="%{label}: %{value:g}%<extra></extra>",
        ))
        figure.update_layout(height=350, showlegend=True, paper_bgcolor=palette["surface"],
                             font=dict(color=palette["text"], size=13), margin=dict(t=25, b=85, l=15, r=15),
                             legend=dict(orientation="h", y=-.08, x=.5, xanchor="center", font_size=12),
                             annotations=[dict(text="별 100개", x=.5, y=.5, showarrow=False, font_size=20)])
        st.plotly_chart(figure, theme=None, width="stretch", key="theory_weights", config={"displayModeBar": False})
        st.caption("배분 · " + " · ".join(f"{label}: {value:g}%" for label, value in
                   zip([v[0] for v in CRITERIA.values()], [share] + [(100 - share) / 4] * 4)))
        st.metric("일사량 환산점수가 80점이라면 종합점수에", f"{80 * share / 100:.0f}점 반영")
        st.write(f"계산은 **80점 × {share}% = {80 * share / 100:.0f}점**이에요. "
                 "미션에서는 단위가 다른 지표를 먼저 0~100점으로 환산하고, 이렇게 반영한 점수를 모두 더합니다.")
        st.success("준비 완료! 이제 사진 속 전문가처럼 자료를 비교하고 나만의 선택을 만들어 봅시다.")

    st.divider()
    previous, following = st.columns(2)
    previous.button("← 이전 설명", disabled=step == 0, on_click=change_theory_step, args=(step - 1,))
    if step < 3:
        following.button("다음 이야기 →", type="primary", on_click=change_theory_step, args=(step + 1,), width="stretch")
    else:
        following.button("준비됐어요! 미션 시작하기 →", type="primary", on_click=finish_theory, width="stretch")
    if st.session_state.theory_completed:
        st.button("이론 닫고 미션으로 돌아가기", on_click=finish_theory)


def show_table(data, hide_index=False, decimals=1, selected=None):
    palette = current_palette()
    styled = data.style.set_properties(**{"background-color": palette["surface"], "color": palette["text"]})
    if selected is not None:
        styled = styled.apply(lambda row: [f"background-color: {palette['soft']}; font-weight: 700"
                                          if row.name == selected else "" for _ in row], axis=1)
    st.dataframe(styled.format(precision=decimals, na_rep="—"), hide_index=hide_index, width="stretch")


def bar_figure(values, title, unit, selected=None, score_axis=False):
    palette = current_palette()
    colors = [palette["yellow"] if site == selected else palette["green"] for site in values.index]
    figure = go.Figure(go.Bar(
        x=values.tolist(), y=values.index.tolist(), orientation="h", marker_color=colors,
        text=[f"{v:.1f}" for v in values], textposition="outside", cliponaxis=False,
        hovertemplate=f"%{{y}}<br>%{{x:.2f}} {unit}<extra></extra>",
    ))
    figure.update_layout(
        title=dict(text=title, font=dict(size=16)), height=310,
        paper_bgcolor=palette["surface"], plot_bgcolor=palette["surface"],
        font=dict(color=palette["text"], family="Noto Sans KR, Malgun Gothic, sans-serif", size=13),
        margin=dict(l=12, r=60, t=48, b=35), showlegend=False,
        hoverlabel=dict(bgcolor=palette["surface"], font_color=palette["text"]),
        xaxis=dict(title=unit, gridcolor=palette["grid"], zeroline=False, rangemode="tozero"),
        yaxis=dict(autorange="reversed", automargin=True, showgrid=False),
    )
    maximum = 100 if score_axis else max(float(values.max()), 1)
    figure.update_xaxes(range=[0, maximum * 1.15])
    return figure


def show_contributions(result, key):
    palette = current_palette()
    figure = go.Figure()
    colors = [palette["yellow"], palette["green"], "#52B8AF", "#6FADDF", "#B095DA"]
    for (criterion, (label, _, _, _)), color in zip(CRITERIA.items(), colors):
        figure.add_bar(name=label, x=result[f"{label} 반영점수"].tolist(), y=result.index.tolist(),
                       orientation="h", marker_color=color,
                       hovertemplate=f"%{{y}}<br>{label}: %{{x:.2f}}점<extra></extra>")
    figure.update_layout(
        title=dict(text="항목별 기여점수", font=dict(size=16)), barmode="stack", height=380,
        paper_bgcolor=palette["surface"], plot_bgcolor=palette["surface"], font=dict(color=palette["text"]),
        margin=dict(l=12, r=15, t=48, b=75), legend=dict(orientation="h", y=-.22, x=0, font_size=11),
        xaxis=dict(title="종합점수에 반영된 점수", range=[0, 100], gridcolor=palette["grid"], zeroline=False),
        yaxis=dict(autorange="reversed", automargin=True),
        hoverlabel=dict(bgcolor=palette["surface"], font_color=palette["text"]),
    )
    st.plotly_chart(figure, theme=None, width="stretch", key=key, config={"displayModeBar": False})


def weight_controls():
    for column, preset in zip(st.columns(3), PRESETS):
        column.button(f"{preset} 적용", on_click=apply_preset, args=(preset,), width="stretch")
    reset, convert = st.columns(2)
    reset.button("기본값 복원", on_click=apply_preset, args=("균형 평가",), width="stretch")
    convert.button("자동 100% 환산", on_click=auto_convert_weights, width="stretch")
    for key, (label, _, _, default) in CRITERIA.items():
        st.session_state[f"_weight_{key}"] = st.session_state.weights[key]
        st.slider(f"{label} 가중치 (%)", 0, 100, step=1, key=f"_weight_{key}",
                  on_change=save_weight, args=(key,), help=f"기본 가중치: {default}%")
    total = sum(st.session_state.weights.values())
    st.metric("가중치 합계", f"{total}%")
    if not valid_weights(st.session_state.weights):
        st.warning("현재 가중치 합계가 100%가 아닙니다. 가중치를 조절하거나 자동 환산 버튼을 사용하세요.")
    if st.session_state.get("weight_notice"):
        st.info(st.session_state.weight_notice)


def show_scoring_method():
    with st.expander("점수는 어떻게 계산하나요? · 정규화와 가중합"):
        st.write("단위가 다른 다섯 지표를 후보지 사이의 **0~100점**으로 환산합니다.")
        st.latex(r"\text{큰 값이 유리: }\quad s=100\frac{x-\min(x)}{\max(x)-\min(x)}")
        st.latex(r"\text{작은 값이 유리: }\quad s=100\frac{\max(x)-x}{\max(x)-\min(x)}")
        st.latex(r"\text{종합점수}=\sum_i s_i\times\frac{w_i}{100}")
        st.caption("일사량·환경 수용성은 클수록, 비용·경사도·전력망 거리는 작을수록 유리합니다. "
                   "한 항목의 값이 모두 같으면 모두 100점입니다. 점수 합산 중에는 반올림하지 않습니다.")
        st.caption("제한 조건을 적용해도 원래 4개 후보로 정규화합니다. 제외된 후보는 순위가 없습니다. "
                   "동점은 공동 순위입니다. 이 상대평가 점수는 실제 사업의 절대적 경제성을 의미하지 않습니다.")
        show_table(normalize_data(DATA).rename(columns={k: v[0] for k, v in CRITERIA.items()}))


def show_result(result, key):
    top = leaders(result)
    if not top:
        st.warning("현재 경사도 제한을 충족하는 후보지가 없습니다. 제한 조건을 다시 검토해 주세요.")
    else:
        name, score = st.columns([3, 1])
        name.metric("현재 1위 후보지" if len(top) == 1 else "공동 1위 후보지", " · ".join(top))
        score.metric("종합점수 / 100", f"{result.loc[top[0], '종합점수']:.1f}점")
        eligible = result.loc[result["평가 대상"], "종합점수"]
        st.plotly_chart(bar_figure(eligible, "후보지 종합점수 비교", "점 / 100", selected=top[0], score_axis=True),
                        theme=None, width="stretch", key=key, config={"displayModeBar": False})
    show_table(result[["순위", "종합점수", "평가 대상", "제외 사유"]])
    if (~result["평가 대상"]).any():
        st.caption("제외 지역의 점수는 비교를 위한 참고값이며 순위에 포함되지 않습니다.")


def experiment_table(max_slope):
    rows = []
    for name, preset in PRESETS.items():
        result = evaluate_sites(preset, max_slope)
        top = leaders(result)
        rows.append({
            "실험": name, "1위 지역": " · ".join(top) if top else "평가 대상 없음",
            "1위 점수": round(float(result.loc[top[0], "종합점수"]), 1) if top else None,
        })
    return pd.DataFrame(rows)


def report_rows(weights, max_slope):
    """요약·전체 답변·원자료·환산점수·세 시나리오를 하나의 보고서에 기록합니다."""
    answers = st.session_state.answers
    result, normalized = evaluate_sites(weights, max_slope), normalize_data(DATA)
    rows = []

    def add(section, item, value, site=""):
        rows.append({"구분": section, "항목": item, "후보 지역": site, "값": value})

    add("보고서", "제목", "SOLAR SITE LAB: 데이터로 찾는 최적의 태양광 발전단지")
    add("보고서", "생성 시각(한국)", datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M"))
    for key, label in [("student_id", "학번"), ("student_name", "이름")]:
        add("학생 정보", label, answers.get(key, ""))
    add("자료 안내", "출처", "수업용 가상 데이터. 실제 지역 조사값이 아닙니다.")
    add("자료 안내", "가정", "모든 후보는 기본 법적 입지 요건을 충족한다고 가정합니다.")
    add("계산 방법", "정규화", "원래 4개 후보 기준 최소–최대 정규화, 동일값 100점, 제외 후 재정규화 없음")
    add("계산 방법", "종합점수", "항목별 환산점수 × 가중치(%) / 100의 합. 동점은 공동 순위.")
    add("입지 제한", "경사도 상한", "적용 안 함" if max_slope is None else f"{max_slope}° 이하 (수업용 사업 조건)")
    add("결과 요약", "자동 계산 1위", " · ".join(leaders(result)) or "평가 대상 없음")
    for key, label in QUESTIONS.items():
        add("학생 답변", label, answers.get(key, ""))
    for key, (label, unit, _, _) in CRITERIA.items():
        add("Q18 최종 가중치", f"{label} (%)", weights[key])
        for site in SITES:
            add("후보지 원자료", f"{label} ({unit})", DATA.loc[site, key], site)
            add("환산점수", label, normalized.loc[site, key], site)
            add("최종 항목별 반영점수", label, result.loc[site, f"{label} 반영점수"], site)
    for site, row in result.iterrows():
        for item in ["순위", "종합점수", "평가 대상", "제외 사유"]:
            add("나의 최종 평가", item, "대상 제외" if pd.isna(row[item]) else row[item], site)
    for name, preset in PRESETS.items():
        for key, value in preset.items():
            add(f"실험 가중치 · {name}", CRITERIA[key][0] + " (%)", value)
        for site, row in evaluate_sites(preset, max_slope).iterrows():
            add(f"실험 결과 · {name}", "종합점수", row["종합점수"], site)
            add(f"실험 결과 · {name}", "순위", "대상 제외" if pd.isna(row["순위"]) else row["순위"], site)
    for _, row in experiment_table(max_slope).iterrows():
        value = row["1위 지역"] if pd.isna(row["1위 점수"]) else f"{row['1위 지역']} / {row['1위 점수']}점"
        add("Q14 실험 비교", row["실험"], value)
    return rows


def csv_report(rows):
    # Excel에서 학생 입력을 수식으로 실행하지 않도록 처리합니다.
    frame = pd.DataFrame(rows)
    for column in frame.columns:
        frame[column] = frame[column].map(
            lambda value: "'" + value if isinstance(value, str)
            and value.lstrip().startswith(("=", "+", "-", "@")) else value
        )
    output = StringIO()
    frame.to_csv(output, index=False)
    return output.getvalue().encode("utf-8-sig")


def txt_report(rows):
    lines = ["SOLAR SITE LAB · 나의 태양광 입지 선정 보고서", "=" * 50]
    section = None
    for row in rows:
        if row["구분"] != section:
            section = row["구분"]
            lines.extend(["", f"[{section}]"])
        site = f" · {row['후보 지역']}" if row["후보 지역"] else ""
        value = row["값"]
        if isinstance(value, float):
            value = f"{value:.1f}"
        lines.append(f"{row['항목']}{site}: {value}")
    return "\n".join(lines).encode("utf-8-sig")


def html_report(rows, result):
    """추가 패키지 없이 그래프를 포함한 인쇄용 HTML을 생성합니다."""
    parts = [
        "<!doctype html><html lang='ko'><meta charset='utf-8'>",
        "<title>SOLAR SITE LAB · 나의 입지 선정 보고서</title>",
        "<style>body{font-family:system-ui,sans-serif;max-width:1000px;margin:40px auto;padding:0 20px;color:#17313b}"
        "table{border-collapse:collapse;width:100%;font-size:13px;margin:16px 0}"
        "th,td{border:1px solid #d7e3e1;padding:8px;text-align:left;white-space:pre-wrap;overflow-wrap:anywhere}"
        "h2{margin-top:32px}svg{max-width:100%;height:auto}"
        "@media print{body{margin:0}h2{break-after:avoid}tr,svg{break-inside:avoid}}</style>",
        "<h1>SOLAR SITE LAB</h1><p>데이터로 찾는 최적의 태양광 발전단지 · 나의 보고서</p>",
        "<p>브라우저에서 인쇄(Ctrl+P)를 선택하면 PDF로 저장할 수 있습니다.</p>",
        "<h2>나의 가중치 적용 결과</h2>",
        "<svg viewBox='0 0 720 220' role='img' aria-label='후보지별 종합점수, 100점 만점'>",
    ]
    for i, (site, row) in enumerate(result.iterrows()):
        y, score = 10 + 48 * i, float(row["종합점수"])
        color = "#16a085" if row["평가 대상"] else "#9ca3af"
        label = f"{score:.2f}점" + (" · 대상 제외" if not row["평가 대상"] else "")
        parts.append(
            f"<text x='0' y='{y + 22}' font-size='14'>{html.escape(site)}</text>"
            f"<rect x='150' y='{y}' width='400' height='30' fill='#edf3f2'/>"
            f"<rect x='150' y='{y}' width='{score * 4:.3f}' height='30' fill='{color}'/>"
            f"<text x='560' y='{y + 22}' font-size='14'>{html.escape(label)}</text>"
        )
    parts.append("<text x='150' y='215' font-size='12'>0점</text>"
                 "<text x='510' y='215' font-size='12'>100점</text></svg>")
    frame = pd.DataFrame(rows)
    for section in frame["구분"].unique():
        parts.append(f"<h2>{html.escape(section)}</h2>")
        parts.append(frame.loc[frame["구분"] == section, ["항목", "후보 지역", "값"]].to_html(
            index=False, escape=True, border=0))
    parts.append("</html>")
    return "".join(parts).encode("utf-8")


def show_report(weights, max_slope, completed):
    st.subheader("나의 결과 보고서")
    missing = [] if answered("student_id", "student_name") else ["학생 정보(학번·이름)"]
    missing.extend(f"MISSION {i + 1:02d} {MISSIONS[i]}" for i, done in enumerate(completed) if not done)
    if missing:
        st.info("보고서를 완성하려면 확인하세요: " + ", ".join(missing))
        st.caption("미션을 자유롭게 오가며 작성하세요. 서술형 답변은 정답 여부가 아닌 작성 여부만 확인합니다.")
    if st.button("나의 결과 보고서 확인하기", type="primary", disabled=bool(missing)):
        st.session_state.report_open = True
    if missing or not st.session_state.get("report_open"):
        return
    st.success("축하합니다! 태양광 발전단지 입지 선정 프로젝트를 완료했습니다.")
    answers = st.session_state.answers
    st.write(f"{answers['student_id']} · {answers['student_name']}")
    first, last = st.columns(2)
    first.metric("최초 예상 지역", answers["initial_site"])
    last.metric("최종 선정 지역", answers["q17"])
    result = evaluate_sites(weights, max_slope)
    show_result(result, key="report_scores")
    show_table(weight_table(weights), hide_index=True)
    for key in ["q19_1", "q19_2", "q20_problem", "q20_solution", "q22", "q23"]:
        st.write(f"**{QUESTIONS[key]}**")
        st.text(answers[key])
    rows = report_rows(weights, max_slope)
    left, middle, right = st.columns(3)
    left.download_button("CSV 보고서 다운로드", csv_report(rows), "solar_site_lab_report.csv", "text/csv")
    middle.download_button("TXT 보고서 다운로드", txt_report(rows), "solar_site_lab_report.txt", "text/plain")
    right.download_button("인쇄용 보고서 다운로드 (HTML → PDF)", html_report(rows, result),
                          "solar_site_lab_report.html", "text/html")
    st.caption("CSV·TXT에는 전체 답변·원자료·가중치·실험별 점수가 포함됩니다. HTML에는 그래프도 포함되며, "
               "브라우저에서 열고 인쇄 → PDF로 저장할 수 있습니다.")


def start_project():
    if answered("student_id", "student_name"):
        st.session_state.project_started = True
        st.session_state.mission = 0
        open_theory()


def main():
    st.set_page_config(page_title="SOLAR SITE LAB | 태양광 입지 선정", page_icon="☀️", layout="wide")
    for key, default in [
        ("answers", {}), ("weights", PRESETS["균형 평가"].copy()),
        ("settings", {"limit_enabled": False, "max_slope": 12}), ("mission", 0), ("appearance", "자동"),
        ("theory_completed", False), ("theory_open", True), ("theory_step", 0), ("theory_share", 30),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default
    if "project_started" not in st.session_state:
        st.session_state.project_started = answered("student_id", "student_name")
    apply_design()
    weights, settings = st.session_state.weights, st.session_state.settings
    max_slope = settings["max_slope"] if settings["limit_enabled"] else None
    completed = completion_status(weights, max_slope)
    with st.sidebar:
        st.markdown('<div class="lab-brand"><span class="lab-sun">☀</span><div class="lab-wordmark">SOLAR SITE LAB'
                    '<small>신재생에너지과 · 디지털 탐구 학습지</small></div></div>', unsafe_allow_html=True)
        st.radio("화면 모드", ["자동", "라이트", "다크"], horizontal=True, key="appearance")
        st.caption("자동 모드는 Streamlit 테마 설정을 따릅니다.")
        text_answer("student_id", "학번", short=True)
        text_answer("student_name", "이름", short=True)
        st.divider()
        st.radio("학습 미션", range(7), key="mission",
                 format_func=lambda i: f"{'✓' if completed[i] else f'{i + 1:02d}'}  {MISSIONS[i]}",
                 disabled=not st.session_state.project_started or not answered("student_id", "student_name")
                 or st.session_state.theory_open or not st.session_state.theory_completed)
        st.caption("✓는 답변 작성 완료를 뜻합니다.")
        if st.session_state.theory_completed:
            st.button("📚 이론 다시 보기", on_click=open_theory, width="stretch")
        st.divider()
        st.caption("답변은 현재 접속 세션에서 유지됩니다. 새로고침이나 서버 재시작으로 사라질 수 있으니 "
                   "완료 후 보고서를 다운로드하세요.")
    mission = st.session_state.mission
    name = st.session_state.answers.get("student_name", "").strip() or "학생"
    in_theory = st.session_state.project_started and (st.session_state.theory_open or not st.session_state.theory_completed)
    stage = f"이론 탐험 {st.session_state.theory_step + 1:02d} / 04" if in_theory else f"MISSION {mission + 1:02d} / 07"
    st.markdown('<div class="lab-topline"><div><strong>☀ SOLAR SITE LAB</strong>'
                '<small>데이터로 찾는 최적의 태양광 발전단지</small></div>'
                f'<div class="lab-badge">{html.escape(name)} · {stage}</div></div>',
                unsafe_allow_html=True)
    st.progress(sum(completed) / 7, text=f"나의 탐구 진행률 {round(sum(completed) / 7 * 100)}% · {sum(completed)}/7개 미션 작성 완료")
    if not st.session_state.project_started or not answered("student_id", "student_name"):
        st.markdown('<div class="lab-kicker">YOUR CLEAN ENERGY MISSION</div>', unsafe_allow_html=True)
        st.title("태양광 발전단지 입지 선정 프로젝트")
        st.write("여러분은 태양광 발전단지 건설 프로젝트의 입지 선정 전문가입니다. "
                 "4개의 후보 지역을 분석하고 가장 적합한 발전단지 위치를 선정해 보세요.")
        show_photo("solar_farm")
        first, second, third = st.columns(3)
        first.metric("탐구할 후보 지역", "4개")
        second.metric("나만의 평가 기준", "5가지")
        third.metric("함께 완성할 미션", "7단계")
        st.info("왼쪽 사이드바에 학번과 이름을 입력한 뒤 시작하세요. 사진과 이야기로 익히는 짧은 이론 탐험을 거쳐 미션을 시작합니다.")
        st.button("프로젝트 시작하기 →", type="primary", on_click=start_project,
                  disabled=not answered("student_id", "student_name"))
        st.caption("모든 후보지 데이터는 수업용 가상 자료입니다. 답변은 현재 세션에서 유지되며 마지막 미션에서 보고서로 저장할 수 있습니다.")
        scroll_to_top_on_navigation("welcome")
        return
    if in_theory:
        show_theory()
        scroll_to_top_on_navigation(f"theory-{st.session_state.theory_step}")
        return
    st.markdown(f'<div class="lab-kicker">MISSION {mission + 1:02d} · {MISSIONS[mission]}</div>', unsafe_allow_html=True)
    st.header(TITLES[mission])
    st.markdown(f'<div class="lab-guide">{MISSION_GUIDES[mission]}</div>', unsafe_allow_html=True)

    if mission == 0:
        show_photo("solar_farm")
        st.info("여러분은 1MW급 태양광 발전단지의 입지 선정 전문가입니다. 네 후보지를 비교하고 "
                "자신만의 기준으로 최적 입지를 선정하세요. 햇빛뿐 아니라 비용·지형·전력망·환경도 함께 살펴봅니다.")
        section_heading("01", "탐구 질문 · 나의 첫 번째 판단")
        choice_answer("q1", ["햇빛이 많이 비치는 지역", "토지 가격이 저렴한 지역", "지형이 평탄한 지역",
                             "전력망과 가까운 지역", "환경에 미치는 영향이 적은 지역"])
        text_answer("q2")
        choice_answer("q3", ["그렇다", "아니다", "잘 모르겠다"], horizontal=True)
        text_answer("q3_reason")
        choice_answer("initial_site", SITES, "분석 전, 이름만 보고 예상하는 최적 지역은 어디인가요?")
        st.caption("이 예상과 Q3 답변을 마지막 단계에서 다시 비교합니다. 아직 정답을 찾을 필요는 없습니다.")

    elif mission == 1:
        section_heading("01", "학습 자료 · 다섯 가지 입지 조건")
        for i, (key, (label, unit, higher, _)) in enumerate(CRITERIA.items(), 1):
            with st.container(border=True, key=f"card_concept_{key}"):
                photograph, explanation = st.columns([1, 1.25], gap="large")
                with photograph:
                    show_photo(CONCEPT_PHOTOS[key])
                with explanation:
                    st.subheader(f"{ICONS[key]} {label}")
                    st.write(CONCEPTS[key])
                    st.caption(f"단위: {unit} · {'클수록' if higher else '작을수록'} 유리")
        section_heading("02", "탐구 질문 · 입지 조건을 이해했나요?")
        st.subheader("Q4. 다음 항목이 증가하면 일반적으로 유리할까요?")
        for key, (label, _, _, _) in CRITERIA.items():
            choice_answer(f"q4_{key}", ["유리함", "불리함"], f"{label} 증가", horizontal=True)
        if st.button("개념 답변 확인하기"):
            st.session_state.concept_feedback = True
        if st.session_state.get("concept_feedback"):
            for key, (label, _, higher, _) in CRITERIA.items():
                answer = st.session_state.answers.get(f"q4_{key}")
                correct = "유리함" if higher else "불리함"
                if answer == correct:
                    st.success(f"{label}: {correct} — 맞았습니다.")
                elif answer:
                    st.info(f"{label}: 일반적으로 {correct}입니다. 위 설명을 다시 확인해 보세요.")
                else:
                    st.warning(f"{label}: 먼저 답변을 선택해 주세요.")
        text_answer("q5")

    elif mission == 2:
        section_heading("01", "사진으로 먼저 만나 보는 네 후보지")
        candidate_gallery(show_values=True)
        sun, cost = st.columns(2)
        sun.metric("☀ 최고 일사량", "4.7", delta="B 구릉지 · kWh/㎡/일", delta_color="off")
        cost.metric("🪙 최저 토지 비용", "4억원", delta="C 해안 저지", delta_color="off")
        section_heading("02", "데이터 탐구 · 네 후보지 비교")
        controls, highlight = st.columns(2)
        with controls:
            criterion = st.selectbox("비교할 지표", list(CRITERIA),
                                     format_func=lambda k: f"{CRITERIA[k][0]} ({CRITERIA[k][1]})")
        with highlight:
            selected = st.selectbox("강조할 후보 지역", SITES, key="compare_site")
        show_table(display_data(), selected=selected)
        label, unit, higher, _ = CRITERIA[criterion]
        st.plotly_chart(bar_figure(DATA[criterion], f"지역별 {label} 비교", unit, selected=selected),
                        theme=None, width="stretch", key="candidate_comparison", config={"displayModeBar": False})
        st.caption(f"단위: {unit} · {'클수록' if higher else '작을수록'} 유리합니다. 노란 막대는 선택한 지역입니다.")
        st.markdown('<div class="lab-note">자료: 수업용 가상 데이터 · 모든 후보는 기본 법적 입지 요건을 충족한다고 가정합니다. '
                    '환경 수용성은 5점이 가장 유리합니다.</div>', unsafe_allow_html=True)
        section_heading("03", "탐구 질문 · 데이터로 판단하기")
        for key in ["q6", "q7", "q8", "q9"]:
            choice_answer(key, SITES, horizontal=True)
        if st.button("데이터 분석 답변 확인하기"):
            st.session_state.data_feedback = True
        if st.session_state.get("data_feedback"):
            for key, site in {"q6": SITES[1], "q7": SITES[2], "q8": SITES[2], "q9": SITES[3]}.items():
                answer = st.session_state.answers.get(key)
                if answer == site:
                    st.success(f"{key.upper()}: {site} — 맞았습니다.")
                elif answer:
                    st.info(f"{key.upper()}: 표를 다시 비교해 보세요. 해당 지역은 {site}입니다.")
                else:
                    st.warning(f"{key.upper()}: 먼저 지역을 선택해 주세요.")
        text_answer("q10", help="일사량과 전력망 거리는 서로 다른 특성입니다. 한 항목이 우수하면 다른 항목도 항상 우수할까요?")
        choice_answer("q11", SITES)
        text_answer("q11_reason")
        with st.expander("확장 활동 · 예상 연간 발전량 계산"):
            st.caption("일사량 수치를 일평균 등가발전시간으로 간주하는 교육용 단순 추정입니다. "
                       "설치 방향·음영·온도·손실을 상세 반영한 실제 발전량 예측이 아닙니다.")
            capacity = st.number_input("설비용량 (MW)", min_value=0.1, max_value=100.0, value=1.0, step=0.1)
            performance = st.slider("성능계수", 0.50, 1.00, 0.80, 0.01)
            st.latex(r"E\,(\mathrm{MWh/년})\approx P\,(\mathrm{MW})\times H\,(\mathrm{h/일})\times365\times PR")
            generation = pd.DataFrame({"예상 연간 발전량 (MWh/년)": DATA["solar"] * capacity * 365 * performance})
            show_table(generation)
            st.plotly_chart(bar_figure(generation.iloc[:, 0], "예상 연간 발전량", "MWh/년"),
                            theme=None, width="stretch", key="annual_generation", config={"displayModeBar": False})

    elif mission == 3:
        section_heading("01", "직접 조작 · 가중치 설계와 즉시 결과")
        controls, preview = st.columns([1, 1.25], gap="large")
        with controls:
            with st.container(border=True, key="card_weights"):
                st.subheader("나의 평가 가중치")
                st.caption("각 항목의 중요도를 정하세요. 직접 조정하거나 자동 환산으로 합계를 100%로 맞출 수 있습니다.")
                weight_controls()
        with preview:
            with st.container(border=True, key="card_weight_preview"):
                st.subheader("실시간 평가 결과")
                if valid_weights(weights):
                    show_result(evaluate_sites(weights, max_slope), key="weights_live_scores")
                else:
                    st.info("합계를 100%로 맞추면 여기에 점수와 순위가 표시됩니다.")
        section_heading("02", "탐구 질문 · 나의 기준 설명하기")
        highest = [CRITERIA[k][0] for k, v in weights.items() if v == max(weights.values())]
        choice_answer("q12", [v[0] for v in CRITERIA.values()])
        if st.session_state.answers.get("q12") and st.session_state.answers["q12"] not in highest:
            st.info("현재 가장 높은 가중치 항목은 " + ", ".join(highest) + "입니다. Q12 답변이나 가중치를 확인하세요.")
        text_answer("q13")
        st.button("종합점수 계산하기 →", type="primary", disabled=not valid_weights(weights),
                  on_click=go_to_mission, args=(4,))
        show_scoring_method()

    elif mission == 4:
        section_heading("01", "실험실 · 기준을 바꾸고 결과 확인하기")
        controls, preview = st.columns([1, 1.25], gap="large")
        with controls:
            with st.container(border=True, key="card_simulation_controls"):
                st.subheader("나의 가중치 실험")
                weight_controls()
        with preview:
            with st.container(border=True, key="card_simulation_preview"):
                if valid_weights(weights):
                    result = evaluate_sites(weights, max_slope)
                    show_result(result, key="simulation_live_scores")
                else:
                    st.info("가중치 합계를 100%로 맞추면 실시간 평가 결과가 표시됩니다.")
        with st.expander("확장 실험 · 경사도 제한 조건"):
            st.subheader("확장 실험 · 입지 제한 조건")
            for key in ["limit_enabled", "max_slope"]:
                st.session_state[f"_setting_{key}"] = settings[key]
            st.checkbox("경사도 상한 적용", key="_setting_limit_enabled",
                        on_change=save_setting, args=("limit_enabled",))
            st.slider("허용 최대 경사도 (°)", 0, 20, key="_setting_max_slope",
                      on_change=save_setting, args=("max_slope",), disabled=not settings["limit_enabled"])
            st.caption("수업용 사업 조건으로 법률상 일률적 기준이 아닙니다. "
                       "12° 이하를 적용하면 B 지역(14°)은 제외됩니다. 최종 보고서에도 반영됩니다.")
        if valid_weights(weights):
            show_contributions(evaluate_sites(weights, max_slope), key="simulation_contributions")
            with st.expander("항목별 반영점수 표 확인"):
                show_table(evaluate_sites(weights, max_slope)[[f"{v[0]} 반영점수" for v in CRITERIA.values()]])
                st.caption("제외 지역도 참고값을 표시하며 순위에는 포함하지 않습니다.")
        section_heading("02", "결과 비교 · 세 가지 고정 평가 기준")
        for tab, (name, values) in zip(st.tabs(list(PRESETS)), PRESETS.items()):
            with tab:
                st.caption(" · ".join(f"{CRITERIA[k][0]} {v}%" for k, v in values.items()))
                show_result(evaluate_sites(values, max_slope), key=f"experiment_{name}")
        st.subheader("Q14. 세 실험의 1위 지역 비교")
        show_table(experiment_table(max_slope), hide_index=True)
        if max_slope is not None:
            st.caption("위 실험 모두 현재 경사도 제한을 적용합니다. 제한을 해제하면 원래 네 지역의 결과를 확인할 수 있습니다.")
        section_heading("03", "탐구 질문 · 결과가 달라진 이유")
        text_answer("q15")
        choice_answer("q16", ["그렇다", "아니다"], horizontal=True)
        text_answer("q16_reason")
        show_scoring_method()

    elif mission == 5:
        section_heading("01", "최종 평가 · 나의 기준과 지역별 순위")
        if valid_weights(weights):
            show_result(evaluate_sites(weights, max_slope), key="final_scores")
        else:
            st.warning("MISSION 4에서 가중치 합계를 100%로 맞춰 주세요.")
        st.info("자동 계산 1위와 다른 지역을 선택해도 괜찮습니다. 데이터를 근거로 선택을 설명하세요. "
                "적용한 입지 제한은 충족해야 합니다.")
        section_heading("02", "최종 판단 · 데이터로 선택 설명하기")
        choice_answer("q17", SITES)
        site = st.session_state.answers.get("q17")
        if site and valid_weights(weights) and site not in leaders(evaluate_sites(weights, max_slope)):
            st.info("자동 평가 결과와 다른 지역을 선택했습니다. 해당 지역을 선택한 이유를 데이터에 근거하여 설명해 보세요.")
        if site and max_slope is not None and DATA.loc[site, "slope"] > max_slope:
            st.error("선택한 지역은 현재 경사도 제한에서 제외됩니다. 지역 또는 MISSION 5의 제한 조건을 다시 검토하세요.")
        st.subheader("Q18. 최종 적용 가중치")
        show_table(weight_table(weights), hide_index=True)
        st.caption("가중치를 바꾸면 이 표와 보고서도 갱신됩니다. " +
                   ("경사도 제한: 적용 안 함" if max_slope is None else f"현재 경사도 제한: {max_slope}° 이하"))
        text_answer("q19_1", help="다른 후보와 수치를 비교하거나 항목별 반영점수로 설명해 보세요.")
        for key in ["q19_2", "q20_problem", "q20_solution"]:
            text_answer(key)

    else:
        answers = st.session_state.answers
        section_heading("01", "나의 변화 · 처음과 마지막을 나란히")
        first, last = st.columns(2)
        first.metric("최초 예상 지역", answers.get("initial_site") or "아직 선택하지 않음")
        last.metric("최종 선정 지역", answers.get("q17") or "아직 선택하지 않음")
        st.caption("데이터를 처음 확인한 뒤의 Q11 선택: " + (answers.get("q11") or "아직 선택하지 않음"))
        st.write("**처음의 생각 다시 보기**")
        st.write("중요하게 생각한 조건: " + (answers.get("q1") or "미작성"))
        st.write("일사량이 가장 높은 지역이 항상 유리할까? → " + (answers.get("q3") or "미작성"))
        st.text(answers.get("q3_reason") or "선택 이유를 아직 작성하지 않았습니다.")
        section_heading("02", "학습 성찰 · 나의 판단 돌아보기")
        choice_answer("q21", ["같다", "다르다"], horizontal=True)
        if answered("initial_site", "q17", "q21"):
            expected = "같다" if answers["initial_site"] == answers["q17"] else "다르다"
            if answers["q21"] != expected:
                st.warning("위의 최초 예상 지역과 최종 선정 지역을 비교하여 Q21 답변을 확인하세요.")
        text_answer("q22")
        text_answer("q23")
        section_heading("03", "탐구 완료 · 나의 결과 보고서")
        show_report(weights, max_slope, completed)

    st.divider()
    previous, following = st.columns(2)
    previous.button("← 이전 미션", disabled=mission == 0, on_click=go_to_mission, args=(mission - 1,))
    following.button("다음 미션 →", disabled=mission == 6, on_click=go_to_mission,
                     args=(mission + 1,), width="stretch", type="primary")
    st.caption("DATA NOTE · 모든 후보지 자료는 수업용 가상 데이터입니다. 실제 지역의 사업성이나 법적 적합성을 나타내지 않습니다.")
    with st.expander("교사용 안내 · 수업 운영 및 평가"):
        st.write("**학생의 목표** · 지역의 일사량과 입지 데이터를 분석하고, 평가 기준을 바꾸면서 "
                 "최적의 태양광 발전단지를 선정합니다.")
        st.table(pd.DataFrame({
            "차시": ["1차시 · 50분", "2차시 · 50분", "3차시 · 50분"],
            "활동": ["MISSION 1~3 · 사전 예상, 핵심 개념, 후보지 비교",
                     "MISSION 4~5 · 가중치 설계, 종합점수, 조건 변경 실험",
                     "MISSION 6~7 · 최종 선정, 근거 작성, 성찰 및 결과 공유"],
        }))
        st.table(pd.DataFrame({
            "평가영역": ["데이터 분석", "가중치 설정과 근거", "실험 비교·해석", "최종 선정과 논리적 설명", "학습 성찰"],
            "배점": [25, 20, 20, 25, 10],
        }))
        st.caption("자동 계산 1위와 다른 지역을 선택해도 논리적인 근거가 있다면 감점하지 않습니다. "
                   "서술형 답변의 타당성은 교사가 평가합니다.")
        st.caption("교육과정 연결: 실제 적용할 전문교과 과목의 2022 개정 교육과정 성취기준을 확인한 뒤 "
                   "수업 계획안에 기재하세요. 특정 성취기준 번호는 임의로 지정하지 않습니다.")
    scroll_to_top_on_navigation(f"mission-{mission}")


if __name__ == "__main__":
    main()
