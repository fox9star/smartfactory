"""
스마트팩토리 설비 스페어파트 지능형 재고관리 시스템 - 고해상도 시각화 차트 생성기
생성 파일:
1. images/spare_parts_analytics_dashboard.png (종합 분석 인포그래픽 대시보드)
2. images/architecture_diagram.png (시스템 데이터 및 의사결정 파이프라인 아키텍처)
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import seaborn as sns

# 한글 폰트 설정
plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'Pretendard', 'NanumGothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_analytics_dashboard():
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=200)
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    
    # 1. ABC-VED 매트릭스 히트맵
    ax1 = axes[0, 0]
    matrix_data = np.array([
        [4, 2, 1],   # A등급 (Vital, Essential, Desirable)
        [1, 3, 2],   # B등급
        [0, 2, 5]    # C등급
    ])
    sns.heatmap(matrix_data, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax1,
                annot_kws={"size": 18, "weight": "bold", "color": "#0f172a"})
    ax1.set_xticklabels(["Vital (치명)", "Essential (중요)", "Desirable (보조)"], fontsize=11, fontweight="bold")
    ax1.set_yticklabels(["A 등급 (고가)", "B 등급 (중가)", "C 등급 (저가)"], fontsize=11, fontweight="bold", rotation=0)
    ax1.set_title("① 부품 다차원 평가 매트릭스 (ABC-VED Matrix)", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    ax1.add_patch(patches.Rectangle((0, 0), 1, 1, fill=False, edgecolor="#ef4444", lw=3.5))
    ax1.text(0.5, 0.2, "★ 집중 관제 타겟", color="#ef4444", fontweight="bold", ha="center", fontsize=10)

    # 2. 간헐적 수요 예측 시계열 (SBA vs Actual vs Dynamic ROP)
    ax2 = axes[0, 1]
    weeks = np.arange(1, 25)
    np.random.seed(42)
    # 간헐적 수요 모사 (대부분 0, 가끔 1~3개)
    actual_demand = np.array([0,0,1,0,0,0,2,0,0,1,0,0,0,0,3,0,0,1,0,0,0,2,0,0])
    sba_forecast = np.array([0.4, 0.35, 0.48, 0.42, 0.38, 0.34, 0.55, 0.49, 0.44, 0.52, 0.46, 0.41, 0.37, 0.33, 0.65, 0.58, 0.52, 0.60, 0.54, 0.48, 0.43, 0.58, 0.51, 0.46])
    dynamic_rop = np.array([2.0, 2.0, 2.0, 2.0, 2.0, 2.5, 2.8, 3.2, 3.5, 3.5, 3.2, 2.8, 2.5, 2.2, 3.8, 4.0, 4.0, 3.8, 3.5, 3.0, 2.5, 2.5, 2.2, 2.0])
    
    ax2.bar(weeks, actual_demand, color="#94a3b8", alpha=0.7, label="실제 부품 출고량 (Actual)")
    ax2.plot(weeks, sba_forecast, color="#2563eb", lw=2.5, marker="o", markersize=4, label="SBA 수요 예측 곡선")
    ax2.plot(weeks, dynamic_rop, color="#ef4444", lw=2.5, linestyle="--", label="예지보전 연계 동적 ROP")
    ax2.set_title("② 간헐적 시계열 수요 예측 & 동적 재주문점(ROP)", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    ax2.set_xlabel("주차 (Weeks)", fontsize=10)
    ax2.set_ylabel("부품 수량 (Units)", fontsize=10)
    ax2.legend(loc="upper right", fontsize=9, framealpha=0.9)
    ax2.grid(True, linestyle=":", alpha=0.6)

    # 3. 설비 헬스 인덱스 vs 고장확률 vs 안전재고 증액 배수
    ax3 = axes[1, 0]
    health_scores = np.linspace(100, 30, 50)
    failure_prob = 1.0 / (1.0 + np.exp((health_scores - 65) / 8.0))  # 로지스틱 고장확률
    safety_stock_multiplier = 1.0 + 0.85 * failure_prob
    
    ax3_twin = ax3.twinx()
    l1 = ax3.plot(health_scores, failure_prob, color="#f59e0b", lw=2.5, label="설비 고장 확률 P(failure)")
    l2 = ax3_twin.plot(health_scores, safety_stock_multiplier, color="#10b981", lw=2.5, linestyle="-.", label="안전재고(SS) 동적 가중치")
    ax3.set_xlim(100, 30)  # 건강도 감소 방향
    ax3.set_xlabel("설비 헬스 스코어 (Health Score: 100 ➔ 30)", fontsize=10, fontweight="bold")
    ax3.set_ylabel("고장 발생 확률 (0 ~ 1.0)", color="#d97706", fontsize=10)
    ax3_twin.set_ylabel("안전재고 배수 (1.0x ~ 1.85x)", color="#059669", fontsize=10)
    ax3.set_title("③ 설비 건전도와 동적 안전재고(SS) 연동 곡선", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    lines = l1 + l2
    labels = [l.get_label() for l in lines]
    ax3.legend(lines, labels, loc="upper right", fontsize=9)
    ax3.grid(True, linestyle=":", alpha=0.6)

    # 4. 경제적 도입 효과 (ROI 워터폴/바 차트)
    ax4 = axes[1, 1]
    categories = ["도입 전 결품 손실", "도입 후 잔여 손실", "재고보관비 절감", "시스템 운영비", "연간 순 편익"]
    values = [120, 12, 38, -40, 106]  # 백만 원 단위
    colors = ["#f87171", "#fbbf24", "#60a5fa", "#94a3b8", "#34d399"]
    bars = ax4.bar(categories, values, color=colors, edgecolor="#1e293b", lw=1.2, width=0.55)
    
    for bar in bars:
        h = bar.get_height()
        va = "bottom" if h >= 0 else "top"
        ax4.text(bar.get_x() + bar.get_width()/2., h + (2 if h >= 0 else -6),
                 f"{int(h):,}백만", ha="center", va=va, fontsize=10, fontweight="bold")
                 
    ax4.axhline(0, color="#64748b", lw=1)
    ax4.set_title("④ 연간 비용 절감 및 경제적 ROI 분석 (+106백만 원 순편익)", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    ax4.set_ylabel("금액 (백만 원)", fontsize=10)
    ax4.tick_params(axis="x", labelsize=9)
    ax4.grid(True, axis="y", linestyle=":", alpha=0.6)

    plt.suptitle("스마트팩토리 설비 스페어파트 지능형 재고관리 종합 분석", fontsize=18, fontweight="bold", y=0.98, color="#0f172a")
    output_path = os.path.join(OUTPUT_DIR, "spare_parts_analytics_dashboard.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"[성공] 대시보드 분석 차트 생성 완료: {output_path}")

def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(15, 6), dpi=200)
    ax.axis("off")
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 6)

    # 박스 그리기 도우미
    def draw_box(x, y, w, h, title, items, bg_color, border_color, title_color="#ffffff"):
        box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.2,rounding_size=0.3",
                                    facecolor=bg_color, edgecolor=border_color, lw=2)
        ax.add_patch(box)
        ax.text(x + w/2, y + h - 0.5, title, ha="center", va="center", fontsize=12, fontweight="bold", color=title_color)
        for i, item in enumerate(items):
            ax.text(x + 0.3, y + h - 1.1 - i*0.45, item, ha="left", va="center", fontsize=9.5, color="#f8fafc")

    # 4단계 파이프라인 박스
    draw_box(0.5, 0.8, 3.2, 4.4, "01. 설비 IoT & 데이터",
             ["• 진동/온도 3축 센서 수집", "• 8대 핵심 제조 설비 건전도", "• 365일 간헐적 출고 이력", "• 20개 부품 마스터 DB"],
             "#1e293b", "#3b82f6")

    draw_box(4.2, 0.8, 3.2, 4.4, "02. AI 예측 & 분류",
             ["• ABC-VED 다차원 등급화", "• Croston & SBA 시계열 모델", "• 복합 포아송 Tweedie 손실", "• WAPE 정밀도 평가 (<25%)"],
             "#1e293b", "#06b6d4")

    draw_box(7.9, 0.8, 3.2, 4.4, "03. 동적 ROP 최적화",
             ["• 설비 헬스 스코어 연동", "• 고장확률 P(f) 실시간 추정", "• 동적 안전재고 SS 수식", "• 스마트 재주문점 ROP 산출"],
             "#1e293b", "#10b981")

    draw_box(11.6, 0.8, 3.0, 4.4, "04. 관제 & 의사결정",
             ["• Streamlit 4-Tab 대시보드", "• 결품 사전 경보 팝업", "• 1-클릭 긴급 발주 승인", "• 연 1억+ 다운타임 회피"],
             "#1e293b", "#f59e0b")

    # 화살표 연결
    arrow_props = dict(arrowstyle="->,head_width=0.4,head_length=0.6", lw=3, color="#60a5fa")
    ax.annotate("", xy=(4.1, 3.0), xytext=(3.8, 3.0), arrowprops=arrow_props)
    ax.annotate("", xy=(7.8, 3.0), xytext=(7.5, 3.0), arrowprops=arrow_props)
    ax.annotate("", xy=(11.5, 3.0), xytext=(11.2, 3.0), arrowprops=arrow_props)

    ax.set_title("스마트팩토리 설비 스페어파트 지능형 재고관리 엔드투엔드 아키텍처", fontsize=16, fontweight="bold", pad=20, color="#0f172a")
    output_path = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"[성공] 아키텍처 다이어그램 생성 완료: {output_path}")

if __name__ == "__main__":
    generate_analytics_dashboard()
    generate_architecture_diagram()
