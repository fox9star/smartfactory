"""
스마트물류 자동화 창고 3D/2D 디지털 트윈 시각화 그래픽 생성기
생성 파일: images/digital_twin_warehouse.png
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# 한글 폰트 설정
plt.rcParams['font.sans-serif'] = ['Malgun Gothic', 'Pretendard', 'NanumGothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_digital_twin_graphic():
    fig, axes = plt.subplots(2, 2, figsize=(16, 11), dpi=200)
    plt.subplots_adjust(hspace=0.35, wspace=0.25)
    
    # 패널 1: 자동화 창고 랙(Rack) 셀별 재고 상태 공간 배치도
    ax1 = axes[0, 0]
    ax1.set_facecolor("#0f172a")
    ax1.set_title("① 스마트물류 창고 랙-베이(Rack-Bay) 셀별 재고 상태", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    
    # 3개 랙 그리기 (Rack-A, Rack-B, Rack-C)
    racks = ["Rack-A (소모품)", "Rack-B (핵심구동)", "Rack-C (센서/전장)"]
    x_starts = [1, 5, 9]
    colors_status = {
        "urgent": "#ef4444",
        "warning": "#f59e0b",
        "normal": "#10b981",
        "empty": "#334155"
    }
    
    # 랙별 셀 상태 매트릭스 (4 Bay x 3 Level)
    rack_data = [
        # Rack A (4x3)
        [["normal", "normal", "normal", "warning"],
         ["normal", "normal", "normal", "normal"],
         ["normal", "warning", "empty", "empty"]],
        # Rack B (4x3) - Vital
        [["urgent", "warning", "normal", "normal"],
         ["urgent", "normal", "normal", "empty"],
         ["normal", "normal", "empty", "empty"]],
        # Rack C (4x3)
        [["normal", "normal", "warning", "normal"],
         ["normal", "normal", "empty", "empty"],
         ["normal", "empty", "empty", "empty"]]
    ]
    
    for r_idx, (r_name, rx) in enumerate(zip(racks, x_starts)):
        # 랙 프레임 외곽선
        ax1.add_patch(patches.Rectangle((rx - 0.2, 0.5), 3.4, 3.8, fill=False, edgecolor="#64748b", lw=2, linestyle="--"))
        ax1.text(rx + 1.5, 4.5, r_name, color="#38bdf8", fontweight="bold", fontsize=10, ha="center")
        
        matrix = rack_data[r_idx]
        for lvl in range(3):  # 3단
            y = 1.0 + lvl * 1.1
            for bay in range(4):  # 4열
                x = rx + bay * 0.8
                st = matrix[lvl][bay]
                c = colors_status[st]
                ax1.add_patch(patches.Rectangle((x, y), 0.7, 0.85, facecolor=c, edgecolor="#ffffff", lw=1.2, alpha=0.9))
                if st == "urgent":
                    ax1.text(x + 0.35, y + 0.42, "🚨", fontsize=10, ha="center", va="center")
                elif st == "warning":
                    ax1.text(x + 0.35, y + 0.42, "⚠️", fontsize=9, ha="center", va="center")
                elif st == "normal":
                    ax1.text(x + 0.35, y + 0.42, "✓", color="#ffffff", fontweight="bold", fontsize=10, ha="center", va="center")

    ax1.set_xlim(0, 13)
    ax1.set_ylim(0, 5.2)
    ax1.axis("off")
    
    # 범례
    ax1.text(1.5, 0.2, "■ 긴급 발주 (Urgent)", color="#ef4444", fontweight="bold", fontsize=9)
    ax1.text(5.0, 0.2, "■ 주의 (Warning)", color="#f59e0b", fontweight="bold", fontsize=9)
    ax1.text(8.0, 0.2, "■ 적정 (Normal)", color="#10b981", fontweight="bold", fontsize=9)
    ax1.text(11.0, 0.2, "■ 여유 (Empty)", color="#94a3b8", fontweight="bold", fontsize=9)

    # 패널 2: AGV 자율주행 무인운반차 관제 및 긴급 출고 경로
    ax2 = axes[0, 1]
    ax2.set_facecolor("#0b0f19")
    ax2.set_title("② AGV 자율 무인운반차 텔레메트리 & 동적 주행 경로", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    
    # 공장 및 창고 레이아웃 바닥선
    ax2.plot([1, 1, 9, 9, 1], [1, 7, 7, 1, 1], color="#334155", lw=2, linestyle=":")
    # AGV 주행 가이드 라인
    ax2.plot([2, 2, 8, 8, 2], [2, 6, 6, 2, 2], color="#38bdf8", lw=3, alpha=0.7)
    
    # 설비 위치 (1라인 EQ-103 유압프레스)
    ax2.add_patch(patches.Rectangle((7.5, 4.5), 1.8, 1.8, facecolor="#1e293b", edgecolor="#ef4444", lw=2.5))
    ax2.text(8.4, 5.4, "🏭 1라인\nEQ-103", color="#f87171", fontweight="bold", fontsize=10, ha="center", va="center")
    
    # 창고 Rack B 위치
    ax2.add_patch(patches.Rectangle((1.5, 4.5), 1.8, 1.8, facecolor="#1e293b", edgecolor="#38bdf8", lw=2))
    ax2.text(2.4, 5.4, "📦 자동창고\nRack-B (SP-102)", color="#38bdf8", fontweight="bold", fontsize=9, ha="center", va="center")
    
    # 충전 도크
    ax2.add_patch(patches.Rectangle((1.5, 1.2), 1.8, 1.2, facecolor="#1e293b", edgecolor="#10b981", lw=2))
    ax2.text(2.4, 1.8, "⚡ 충전 도크\n(AGV-03)", color="#34d399", fontweight="bold", fontsize=9, ha="center", va="center")
    
    # AGV-01 이동 화살표 (긴급 피킹 경로)
    ax2.annotate("", xy=(7.2, 5.4), xytext=(3.5, 5.4),
                 arrowprops=dict(arrowstyle="->", color="#ef4444", lw=3.5, mutation_scale=20))
    ax2.add_patch(patches.Circle((5.2, 5.4), 0.45, facecolor="#ef4444", edgecolor="#ffffff", lw=1.5))
    ax2.text(5.2, 5.4, "AGV1", color="#ffffff", fontweight="bold", fontsize=8, ha="center", va="center")
    ax2.text(5.2, 6.1, "🚨 SP-102 긴급 이송 중\n(속도: 1.4m/s, 배터리: 89%)", color="#ef4444", fontweight="bold", fontsize=8.5, ha="center")
    
    # AGV-02 (정기 입고)
    ax2.add_patch(patches.Circle((7.0, 2.0), 0.4, facecolor="#3b82f6", edgecolor="#ffffff", lw=1.5))
    ax2.text(7.0, 2.0, "AGV2", color="#ffffff", fontweight="bold", fontsize=8, ha="center", va="center")
    ax2.text(7.0, 1.3, "📦 정기 입고 적재 (74%)", color="#60a5fa", fontweight="bold", fontsize=8.5, ha="center")

    ax2.set_xlim(0.5, 10.5)
    ax2.set_ylim(0.5, 7.5)
    ax2.axis("off")

    # 패널 3: 골든존(Golden Zone) 공간 최적화 및 랙 단별 배치 전략
    ax3 = axes[1, 0]
    levels = ["3단 (상단: 경량/소형)", "2단 (골든존: 고빈도 출고)", "1단 (하단: 중량물/대형)"]
    y_pos = [2, 1, 0]
    weights = [25, 55, 20]  # 출고 작업 비중
    colors = ["#60a5fa", "#f59e0b", "#34d399"]
    
    bars = ax3.barh(y_pos, weights, color=colors, height=0.55, edgecolor="#1e293b", lw=1.5)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(levels, fontsize=10, fontweight="bold")
    ax3.set_xlabel("월간 출고 피킹 작업 비중 (%)", fontsize=10)
    ax3.set_title("③ 인체공학 & 물류 효율 중심 랙 수직 공간 배치 (골든존 전략)", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    ax3.set_xlim(0, 70)
    
    for bar, w in zip(bars, weights):
        ax3.text(w + 1.5, bar.get_y() + bar.get_height()/2, f"{w}% (최적 배치)", va="center", fontsize=10, fontweight="bold", color="#1e293b")
    ax3.grid(axis="x", linestyle=":", alpha=0.6)

    # 패널 4: 스마트물류 IoT 창고 환경 모니터링 텔레메트리 (온도/습도/점유율)
    ax4 = axes[1, 1]
    metrics = ["공간 점유율\n(Occupancy)", "평균 온도\n(20.8°C)", "평균 습도\n(41.5% RH)", "AGV 가동률\n(Fleet Active)"]
    values = [68.4, 69.3, 55.3, 66.7]  # 시각화용 정규화 스코어
    display_texts = ["68.4%\n(20/36 Bins)", "20.8 °C\n(항온 정상)", "41.5 %RH\n(항습 정상)", "66.7%\n(2/3대 가동)"]
    colors4 = ["#3b82f6", "#10b981", "#06b6d4", "#8b5cf6"]
    
    bars4 = ax4.bar(metrics, values, color=colors4, width=0.55, edgecolor="#1e293b", lw=1.5)
    ax4.set_ylim(0, 100)
    ax4.set_ylabel("지표 상태 지수 (0 ~ 100)", fontsize=10)
    ax4.set_title("④ 창고 IoT 센서 텔레메트리 실시간 현황", fontsize=13, fontweight="bold", pad=12, color="#1e3a8a")
    
    for bar, txt in zip(bars4, display_texts):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3, txt, ha="center", fontsize=9, fontweight="bold", color="#1e293b")
    ax4.grid(axis="y", linestyle=":", alpha=0.6)

    output_path = os.path.join(OUTPUT_DIR, "digital_twin_warehouse.png")
    plt.savefig(output_path, bbox_inches="tight")
    plt.close()
    print(f"Digital Twin Graphic Saved: {output_path}")

if __name__ == "__main__":
    generate_digital_twin_graphic()
