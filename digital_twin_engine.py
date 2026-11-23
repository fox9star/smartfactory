"""
스마트팩토리 설비 스페어파트 스마트물류 디지털 트윈(Digital Twin) 엔진
- 3D/2D 가상 창고 공간 모델링 (Rack-Bay-Level 3D 좌표계)
- 랙 셀(Bin)별 실시간 재고 적재율 및 결품 위험도 시각화
- AGV(무인 이송 로봇) 실시간 관제 및 긴급 출고 경로 시뮬레이션
- 창고 온습도 IoT 센서 텔레메트리 연동
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. 랙 및 셀(Bin) 공간 배치 좌표계 정의
RACK_CONFIG = {
    "Rack-A": {
        "name": "Rack-A (소모품/패스트무버)",
        "desc": "베어링, 필터, O링, 벨트 등 C/D 등급 고회전율 부품",
        "x_offset": 2.0,
        "color_accent": "#3b82f6"
    },
    "Rack-B": {
        "name": "Rack-B (핵심 구동계/중량물)",
        "desc": "AC 서보모터, 유압펌프, 감속기 등 A/V 등급 Vital 핵심부품",
        "x_offset": 6.0,
        "color_accent": "#ef4444"
    },
    "Rack-C": {
        "name": "Rack-C (센서/전장/제어기)",
        "desc": "솔레노이드 밸브, 압력센서, PLC 모듈 등 B/E 등급 정밀 전장부품",
        "x_offset": 10.0,
        "color_accent": "#10b981"
    }
}

NUM_BAYS = 4    # 베이 (열: 1~4 Bay, Y축 방향)
NUM_LEVELS = 3  # 레벨 (단: 1~3 Level, Z축 방향)


def build_warehouse_digital_twin_data(df_inventory_results):
    """
    부품 분석 결과(df_inventory_results)를 3차원 창고 셀에 공간 매핑
    """
    bins = []
    part_idx = 0
    total_parts = len(df_inventory_results)
    
    # 3개 랙, 각 4 Bay x 3 Level = 36개 보관 셀(Bin)
    for rack_id, rack_info in RACK_CONFIG.items():
        x = rack_info["x_offset"]
        
        for bay in range(1, NUM_BAYS + 1):
            y = bay * 2.5  # 2.5m 간격
            
            for level in range(1, NUM_LEVELS + 1):
                z = level * 1.8  # 1.8m 높이 간격
                bin_id = f"BIN-{rack_id[-1]}-{bay:02d}-{level:02d}"
                
                # 부품 매핑 (20개 부품 배치, 나머지는 빈 셀/여유 공간)
                if part_idx < total_parts:
                    p = df_inventory_results.iloc[part_idx]
                    part_id = p["part_id"]
                    part_name = p["part_name"]
                    category = p["category"]
                    abc_grade = p["abc_grade"]
                    ved_grade = p["ved_grade"]
                    current_stock = int(p["current_stock"])
                    dynamic_ss = int(p["dynamic_ss"])
                    dynamic_rop = int(p["dynamic_rop"])
                    status = p["status"]
                    equip_prob = float(p.get("equip_failure_prob", 0.0))
                    part_idx += 1
                else:
                    part_id = "EMPTY"
                    part_name = "(빈 셀 - 여유 보관 공간)"
                    category = "Empty"
                    abc_grade = "-"
                    ved_grade = "-"
                    current_stock = 0
                    dynamic_ss = 0
                    dynamic_rop = 0
                    status = "여유 공간 (Empty)"
                    equip_prob = 0.0
                
                max_capacity = 30 if part_id != "EMPTY" else 30
                fill_rate = min(100.0, (current_stock / max_capacity * 100.0)) if max_capacity > 0 else 0.0
                
                bins.append({
                    "bin_id": bin_id,
                    "rack_id": rack_id,
                    "rack_name": rack_info["name"],
                    "bay": bay,
                    "level": level,
                    "x": x,
                    "y": y,
                    "z": z,
                    "part_id": part_id,
                    "part_name": part_name,
                    "category": category,
                    "abc_grade": abc_grade,
                    "ved_grade": ved_grade,
                    "current_stock": current_stock,
                    "dynamic_ss": dynamic_ss,
                    "dynamic_rop": dynamic_rop,
                    "max_capacity": max_capacity,
                    "fill_rate": round(fill_rate, 1),
                    "status": status,
                    "equip_failure_prob": round(equip_prob, 2),
                    "temp_c": round(20.5 + np.random.uniform(-0.8, 0.8), 1),
                    "humidity_pct": round(42.0 + np.random.uniform(-2.0, 2.0), 1),
                    "rfid_tag": f"RFID-{rack_id[-1]}{bay}{level}-{100 + part_idx}"
                })
                
    df_bins = pd.DataFrame(bins)
    return df_bins


def get_agv_fleet_status():
    """
    창고 내 자율주행 무인운반차(AGV) 실시간 텔레메트리 데이터
    """
    agvs = [
        {
            "agv_id": "AGV-01",
            "name": "고속 피킹 AGV 1호기",
            "status": "🚨 긴급 피킹 중",
            "mission": "긴급 출고: SP-102 (AC 서보모터) ➔ 1라인 EQ-103 유압프레스 공급",
            "battery_pct": 89,
            "speed_mps": 1.4,
            "current_x": 6.0,
            "current_y": 5.2,
            "target_bin": "BIN-B-02-01",
            "state_color": "#ef4444"
        },
        {
            "agv_id": "AGV-02",
            "name": "중량물 이송 AGV 2호기",
            "status": "📦 정기 입고 적재",
            "mission": "정기 입고: SP-101 (스핀들 베어링 20ea) ➔ Rack-A 입고 진행 중",
            "battery_pct": 74,
            "speed_mps": 0.8,
            "current_x": 2.0,
            "current_y": 7.5,
            "target_bin": "BIN-A-03-02",
            "state_color": "#3b82f6"
        },
        {
            "agv_id": "AGV-03",
            "name": "순찰/검사 AGV 3호기",
            "status": "⚡ 무선 충전 대기",
            "mission": "충전 도크 대기 중 (RFID 자동 스캔 순찰 대기)",
            "battery_pct": 98,
            "speed_mps": 0.0,
            "current_x": 0.5,
            "current_y": 1.0,
            "target_bin": "DOCK-01",
            "state_color": "#10b981"
        }
    ]
    return pd.DataFrame(agvs)


def get_warehouse_telemetry():
    """
    창고 환경 IoT 실시간 센서 지표
    """
    return {
        "avg_temp": 20.8,
        "avg_humidity": 41.5,
        "fire_hazard_level": "Safe (정상)",
        "space_occupancy_pct": 68.4,
        "active_agv_count": 2,
        "total_bins": 36,
        "occupied_bins": 20,
        "empty_bins": 16
    }


def create_3d_warehouse_plot(df_bins, df_agv, theme_mode="Dark"):
    """
    Plotly 3D 공간 좌표계 기반 스마트물류 디지털 트윈 시각화
    """
    is_dark = theme_mode in ["Dark", "Gray"]
    bg_color = "#0b0f19" if is_dark else "#f8fafc"
    grid_color = "#334155" if is_dark else "#e2e8f0"
    text_color = "#f1f5f9" if is_dark else "#1e293b"
    
    fig = go.Figure()

    # 1. 상태별 색상 맵
    color_map = {
        "🚨 긴급 발주 (Urgent)": "#ef4444",
        "⚠️ 주의 (Warning)": "#f59e0b",
        "✅ 적정 (Normal)": "#10b981",
        "여유 공간 (Empty)": "#475569" if is_dark else "#cbd5e1"
    }

    # 2. 랙 셀(Bin) 3D 마커 추가
    for status_label, color in color_map.items():
        subset = df_bins[df_bins["status"] == status_label]
        if subset.empty:
            continue
        
        hover_text = [
            f"<b>📍 셀 위치:</b> {row['bin_id']}<br>"
            f"<b>📦 부품명:</b> {row['part_name']} ({row['part_id']})<br>"
            f"<b>🏷️ 등급:</b> ABC={row['abc_grade']} / VED={row['ved_grade']}<br>"
            f"<b>📊 재고:</b> {row['current_stock']}개 / 적재율 {row['fill_rate']}%<br>"
            f"<b>🚨 안전재고(SS):</b> {row['dynamic_ss']}개 (ROP: {row['dynamic_rop']}개)<br>"
            f"<b>⚠️ 설비고장확률:</b> {row['equip_failure_prob']}<br>"
            f"<b>🌡️ 환경:</b> {row['temp_c']}°C, {row['humidity_pct']}% RH<br>"
            f"<b>📡 RFID:</b> {row['rfid_tag']}"
            for _, row in subset.iterrows()
        ]

        fig.add_trace(go.Scatter3d(
            x=subset["x"],
            y=subset["y"],
            z=subset["z"],
            mode="markers+text",
            name=status_label,
            text=subset["bin_id"].apply(lambda s: s.replace("BIN-", "")),
            textposition="top center",
            textfont=dict(size=8, color=text_color),
            marker=dict(
                size=12 if status_label != "여유 공간 (Empty)" else 7,
                color=color,
                symbol="square",
                opacity=0.9 if status_label != "여유 공간 (Empty)" else 0.4,
                line=dict(color="#ffffff" if is_dark else "#000000", width=1)
            ),
            hoverinfo="text",
            hovertext=hover_text
        ))

    # 3. 랙 기둥/프레임 와이어프레임 라인 생성 (물리적 선반 형상화)
    for rack_id, rack_info in RACK_CONFIG.items():
        rx = rack_info["x_offset"]
        for bay in range(1, NUM_BAYS + 1):
            by = bay * 2.5
            fig.add_trace(go.Scatter3d(
                x=[rx, rx],
                y=[by, by],
                z=[0.5, NUM_LEVELS * 1.8 + 0.3],
                mode="lines",
                showlegend=False,
                line=dict(color="#64748b", width=3, dash="dot"),
                hoverinfo="none"
            ))

    # 4. AGV 무인 운반차 위치 및 이동 궤적 표시
    agv_hover = [
        f"<b>🤖 {row['name']}</b> ({row['agv_id']})<br>"
        f"<b>상태:</b> {row['status']}<br>"
        f"<b>임무:</b> {row['mission']}<br>"
        f"<b>배터리:</b> {row['battery_pct']}% | <b>속도:</b> {row['speed_mps']} m/s"
        for _, row in df_agv.iterrows()
    ]
    
    fig.add_trace(go.Scatter3d(
        x=df_agv["current_x"],
        y=df_agv["current_y"],
        z=[0.2] * len(df_agv),
        mode="markers+text",
        name="🤖 자율주행 AGV",
        text=df_agv["agv_id"],
        textposition="bottom center",
        textfont=dict(size=11, color="#38bdf8", family="Arial Black"),
        marker=dict(
            size=15,
            color=["#ef4444", "#3b82f6", "#10b981"],
            symbol="diamond",
            opacity=1.0,
            line=dict(color="#ffffff", width=2)
        ),
        hoverinfo="text",
        hovertext=agv_hover
    ))

    # 5. AGV 주행 유도로 (바닥 트랙 라인)
    fig.add_trace(go.Scatter3d(
        x=[0.5, 6.0, 6.0, 10.0, 10.0, 0.5, 0.5],
        y=[1.0, 1.0, 10.5, 10.5, 1.0, 1.0, 10.5],
        z=[0.05] * 7,
        mode="lines",
        name="AGV 스마트 주행 유도로",
        line=dict(color="#38bdf8", width=4),
        hoverinfo="none"
    ))

    # 레이아웃 스타일 설정
    fig.update_layout(
        title=dict(
            text="🏢 스마트물류 3D 디지털 트윈 공간 뷰 (Smart Warehouse Digital Twin 3D)",
            font=dict(size=16, color=text_color)
        ),
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        scene=dict(
            xaxis=dict(title="창고 X축 (Aisle/랙 위치)", backgroundcolor=bg_color, gridcolor=grid_color, showbackground=True),
            yaxis=dict(title="창고 Y축 (Bay 열 위치)", backgroundcolor=bg_color, gridcolor=grid_color, showbackground=True),
            zaxis=dict(title="창고 Z축 (Level 선반 단)", backgroundcolor=bg_color, gridcolor=grid_color, showbackground=True),
            camera=dict(
                eye=dict(x=-1.6, y=-1.8, z=1.5),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode="manual",
            aspectratio=dict(x=1.2, y=1.5, z=0.8)
        ),
        margin=dict(l=0, r=0, b=0, t=40),
        legend=dict(
            font=dict(color=text_color),
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig


def create_rack_elevation_chart(df_bins, selected_rack="Rack-B", theme_mode="Dark"):
    """
    선택된 랙의 전면 입면도 (Bay x Level 2D 매트릭스 뷰)
    """
    is_dark = theme_mode in ["Dark", "Gray"]
    subset = df_bins[df_bins["rack_id"] == selected_rack].copy()
    
    fig = px.scatter(
        subset,
        x="bay",
        y="level",
        size="fill_rate",
        color="status",
        text="part_name",
        hover_name="bin_id",
        hover_data={"current_stock": True, "dynamic_ss": True, "fill_rate": True, "rfid_tag": True},
        title=f"📋 {RACK_CONFIG[selected_rack]['name']} 단/열 입면 매트릭스",
        labels={"bay": "Bay (열)", "level": "Level (단: 1단=중량물, 3단=경량물)"},
        color_discrete_map={
            "🚨 긴급 발주 (Urgent)": "#ef4444",
            "⚠️ 주의 (Warning)": "#f59e0b",
            "✅ 적정 (Normal)": "#10b981",
            "여유 공간 (Empty)": "#64748b"
        },
        size_max=32
    )
    
    fig.update_traces(textposition="top center", textfont_size=9)
    fig.update_layout(
        paper_bgcolor="#0b0f19" if is_dark else "#ffffff",
        plot_bgcolor="#111827" if is_dark else "#f8fafc",
        font=dict(color="#f1f5f9" if is_dark else "#1e293b"),
        yaxis=dict(tickmode="linear", tick0=1, dtick=1),
        xaxis=dict(tickmode="linear", tick0=1, dtick=1),
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


if __name__ == "__main__":
    from forecast_engine import run_full_inventory_analysis
    df_results, df_parts, df_equip, df_trans = run_full_inventory_analysis()
    df_bins = build_warehouse_digital_twin_data(df_results)
    df_agv = get_agv_fleet_status()
    telemetry = get_warehouse_telemetry()
    print(f"Digital Twin Initialized: {len(df_bins)} bins generated.")
    print("Telemetry:", telemetry)
    print("AGV Fleet:\n", df_agv[["agv_id", "status", "mission"]])
