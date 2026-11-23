"""
스마트팩토리 설비 스페어파트 지능형 재고관리 시스템 - 모의 데이터셋 생성기
4대 핵심 테이블: Part_Master, Equipment_Master, Part_Transactions, Purchase_Orders
CSV 파일 및 SQLite DB(data/spare_parts.db)로 저장
"""

import os
import sqlite3
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 난수 시드 고정 (재현성)
np.random.seed(42)
random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_datasets():
    print("[1/4] Generating Part Master...")
    # 20개 대표 산업용 스페어파트 마스터
    parts_data = [
        # (ID, Name, Category, Unit Cost, Lead Time Mean, Lead Time Std, Current Stock, ABC, VED, Service Level)
        ("SP-101", "고속 스핀들 베어링", "Motor & Drive", 450000, 14, 2.5, 3, "A", "V", 0.99),
        ("SP-102", "AC 서보 모터 750W", "Motor & Drive", 850000, 21, 4.0, 1, "A", "V", 0.99),
        ("SP-103", "산업용 인버터 드라이브", "Motor & Drive", 620000, 18, 3.0, 2, "A", "V", 0.99),
        ("SP-104", "정밀 플렉시블 커플링", "Motor & Drive", 120000, 7, 1.5, 5, "B", "E", 0.95),
        ("SP-201", "비례 공압 제어 밸브", "Pneumatic/Hydraulic", 380000, 12, 2.0, 2, "A", "V", 0.98),
        ("SP-202", "솔레노이드 밸브 5포트", "Pneumatic/Hydraulic", 75000, 5, 1.0, 8, "B", "E", 0.95),
        ("SP-203", "유압 실린더 패킹 키트", "Pneumatic/Hydraulic", 95000, 6, 1.0, 6, "B", "E", 0.95),
        ("SP-204", "에어 필터 레귤레이터", "Pneumatic/Hydraulic", 42000, 3, 0.5, 12, "C", "D", 0.90),
        ("SP-301", "3축 가속도 진동 센서", "Sensor & Control", 310000, 10, 2.0, 2, "A", "E", 0.98),
        ("SP-302", "적외선 표면 온도 센서", "Sensor & Control", 180000, 8, 1.5, 4, "B", "E", 0.95),
        ("SP-303", "고정밀 레이저 변위 센서", "Sensor & Control", 550000, 15, 3.0, 1, "A", "V", 0.99),
        ("SP-304", "PLC 디지털 I/O 모듈", "Sensor & Control", 240000, 10, 2.0, 3, "B", "V", 0.98),
        ("SP-401", "정밀 볼 스크류 어셈블리", "Transmission", 780000, 25, 5.0, 1, "A", "V", 0.99),
        ("SP-402", "우레탄 타이밍 벨트 T10", "Transmission", 35000, 4, 1.0, 15, "C", "E", 0.92),
        ("SP-403", "더블 피치 롤러 체인", "Transmission", 48000, 5, 1.0, 10, "C", "E", 0.92),
        ("SP-404", "유성 감속기 기어 세트", "Transmission", 920000, 30, 6.0, 1, "A", "V", 0.99),
        ("SP-501", "고속 반도체 보호 퓨즈", "Electrical", 18000, 2, 0.5, 25, "C", "D", 0.90),
        ("SP-502", "모터 카본 브러쉬 세트", "Electrical", 28000, 3, 0.5, 18, "C", "D", 0.90),
        ("SP-503", "내열 실리콘 개스킷 패킹", "Consumables", 15000, 3, 0.5, 30, "C", "D", 0.90),
        ("SP-504", "고압 내유성 에어 호스 10m", "Consumables", 22000, 2, 0.5, 20, "C", "D", 0.90),
    ]

    df_parts = pd.DataFrame(parts_data, columns=[
        "part_id", "part_name", "category", "unit_cost_krw", "lead_time_days",
        "lead_time_std", "current_stock", "abc_grade", "ved_grade", "target_service_level"
    ])

    print("[2/4] Generating Equipment Master...")
    # 8개 주요 공정 설비
    equip_data = [
        ("EQ-101", "CNC 정밀선반 1호기", "가공 1라인", "Critical", "2021-03-15", 88.5, 0.08, "Normal"),
        ("EQ-102", "다이캐스팅 주조기 2호기", "주조 라인", "Critical", "2020-08-10", 64.2, 0.62, "Warning"),
        ("EQ-103", "500톤 유압 프레스 1호기", "프레스 라인", "Critical", "2019-11-20", 52.0, 0.85, "Critical"),
        ("EQ-104", "도장 다관절 로봇 1호기", "도장 라인", "Major", "2022-01-18", 91.0, 0.04, "Normal"),
        ("EQ-105", "SMT 고속 칩 마운터", "전자조립 라인", "Critical", "2023-05-12", 94.3, 0.03, "Normal"),
        ("EQ-106", "진공 열처리로 1호기", "열처리 라인", "Major", "2021-09-05", 71.8, 0.38, "Warning"),
        ("EQ-107", "자동 나사 체결 로봇", "최종조립 라인", "Standard", "2022-07-22", 89.0, 0.07, "Normal"),
        ("EQ-108", "사출성형기 1호기", "성형 라인", "Critical", "2020-04-30", 58.7, 0.74, "Critical"),
    ]

    df_equip = pd.DataFrame(equip_data, columns=[
        "equip_id", "equip_name", "line_name", "criticality", "install_date",
        "health_score", "failure_prob", "status"
    ])

    print("[3/4] Generating Historical Part Transactions (Past 365 Days)...")
    # 과거 1년간 부품 출고 이력 (간헐적 시계열 모사)
    end_date = datetime(2026, 11, 23)
    start_date = end_date - timedelta(days=365)
    
    transactions = []
    trans_id = 1000

    # 각 부품별 수요 특성 시뮬레이션
    for _, part in df_parts.iterrows():
        p_id = part["part_id"]
        ved = part["ved_grade"]
        abc = part["abc_grade"]
        cost = part["unit_cost_krw"]

        # VED 및 ABC에 따라 출고 빈도 결정 (Vital/A는 드물지만 중요함)
        if ved == "V":
            # 평균 20~40일에 한 번 1~2개 출고
            event_prob = 0.035
            qty_choices = [1, 1, 1, 2]
        elif ved == "E":
            # 평균 10~20일에 한 번 1~3개 출고
            event_prob = 0.08
            qty_choices = [1, 2, 2, 3]
        else: # Desirable / C
            # 평균 3~7일에 한 번 2~8개 출고
            event_prob = 0.22
            qty_choices = [2, 3, 4, 5, 8]

        current_dt = start_date
        while current_dt <= end_date:
            if random.random() < event_prob:
                qty = random.choice(qty_choices)
                eq = random.choice(df_equip["equip_id"].tolist())
                reason = random.choices(
                    ["정기보전", "돌발고장", "예방교체", "일상점검"],
                    weights=[0.35, 0.30, 0.25, 0.10]
                )[0]
                
                trans_id += 1
                transactions.append((
                    f"TR-{trans_id}",
                    current_dt.strftime("%Y-%m-%d"),
                    p_id,
                    eq,
                    qty,
                    reason,
                    cost,
                    qty * cost
                ))
            current_dt += timedelta(days=1)

    df_trans = pd.DataFrame(transactions, columns=[
        "trans_id", "trans_date", "part_id", "equip_id", "qty_issued",
        "reason", "unit_cost", "total_cost"
    ])

    print("[4/4] Generating Purchase Orders...")
    # 발주 이력 및 미입고(In-Transit/Pending) 발주
    po_list = []
    po_id = 5000
    
    # 최근 1년간 각 부품별 4~12회 발주
    for _, part in df_parts.iterrows():
        p_id = part["part_id"]
        lt = part["lead_time_days"]
        cost = part["unit_cost_krw"]
        n_orders = random.randint(3, 8)

        for _ in range(n_orders):
            days_ago = random.randint(5, 350)
            order_dt = end_date - timedelta(days=days_ago)
            actual_lt = max(1, int(np.random.normal(lt, part["lead_time_std"])))
            expected_dt = order_dt + timedelta(days=lt)
            
            # 발주일 + 실제 리드타임이 현재 날짜보다 이전이면 입고 완료, 아니면 배송중
            arrival_dt = order_dt + timedelta(days=actual_lt)
            if arrival_dt <= end_date:
                status = "Delivered"
                actual_date_str = arrival_dt.strftime("%Y-%m-%d")
            else:
                status = "In-Transit"
                actual_date_str = None

            order_qty = random.choice([2, 4, 5, 10]) if part["abc_grade"] != "A" else random.choice([1, 2, 3])
            po_id += 1
            po_list.append((
                f"PO-{po_id}",
                p_id,
                order_dt.strftime("%Y-%m-%d"),
                expected_dt.strftime("%Y-%m-%d"),
                actual_date_str,
                order_qty,
                cost,
                order_qty * cost,
                status
            ))

    df_po = pd.DataFrame(po_list, columns=[
        "po_id", "part_id", "order_date", "expected_date", "actual_date",
        "order_qty", "unit_cost", "total_amount", "status"
    ])

    # CSV 파일 저장
    df_parts.to_csv(os.path.join(DATA_DIR, "part_master.csv"), index=False, encoding="utf-8-sig")
    df_equip.to_csv(os.path.join(DATA_DIR, "equipment_master.csv"), index=False, encoding="utf-8-sig")
    df_trans.to_csv(os.path.join(DATA_DIR, "part_transactions.csv"), index=False, encoding="utf-8-sig")
    df_po.to_csv(os.path.join(DATA_DIR, "purchase_orders.csv"), index=False, encoding="utf-8-sig")

    # SQLite DB 저장
    db_path = os.path.join(DATA_DIR, "spare_parts.db")
    conn = sqlite3.connect(db_path)
    df_parts.to_sql("part_master", conn, if_exists="replace", index=False)
    df_equip.to_sql("equipment_master", conn, if_exists="replace", index=False)
    df_trans.to_sql("part_transactions", conn, if_exists="replace", index=False)
    df_po.to_sql("purchase_orders", conn, if_exists="replace", index=False)
    conn.close()

    print(f"\n[성공] 데이터셋 생성 완료!")
    print(f" - 부품 마스터: {len(df_parts)}건")
    print(f" - 설비 마스터: {len(df_equip)}건")
    print(f" - 출고 이력: {len(df_trans)}건")
    print(f" - 발주 이력: {len(df_po)}건")
    print(f" - 저장 위치: {DATA_DIR} 및 SQLite ({db_path})")

if __name__ == "__main__":
    generate_datasets()
