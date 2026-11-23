"""
스마트팩토리 설비 스페어파트 지능형 재고관리 시스템 - 수요 예측 및 재고 최적화 엔진
1. 간헐적 시계열 수요 예측 (Croston's Method, SBA, Moving Average)
2. 설비 예지보전(PdM) 연계 동적 안전재고(Dynamic SS) 및 재주문점(Dynamic ROP) 최적화
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from scipy.stats import norm

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def croston_method(series, alpha=0.15):
    """
    Croston's Method for intermittent demand forecasting.
    수요 크기(z_t)와 발생 간격(p_t)을 분리하여 지수평활 추정
    """
    y = np.array(series, dtype=float)
    n = len(y)
    if n == 0:
        return np.array([0.0])
    
    # 첫 양수 수요 인덱스 탐색
    first_idx = np.where(y > 0)[0]
    if len(first_idx) == 0:
        return np.zeros(n)
    
    first = first_idx[0]
    z = y[first]  # 초기 수요량
    p = 1.0       # 초기 수요 간격
    q = 1         # 간격 카운터
    
    forecast = np.zeros(n)
    
    for t in range(first, n):
        if y[t] > 0:
            z = alpha * y[t] + (1 - alpha) * z
            p = alpha * q + (1 - alpha) * p
            q = 1
        else:
            q += 1
        forecast[t] = z / p if p > 0 else 0.0
        
    return forecast

def sba_method(series, alpha=0.15):
    """
    Syntetos-Boylan Approximation (SBA).
    Croston 모델의 과대추정 편향을 (1 - alpha/2) 상수로 보정
    """
    croston_fc = croston_method(series, alpha)
    return (1.0 - alpha / 2.0) * croston_fc

def moving_average(series, window=4):
    """단순 이동평균 (비교 베이스라인)"""
    s = pd.Series(series)
    return s.rolling(window=window, min_periods=1).mean().values

def evaluate_forecast(actual, predicted):
    """예측 평가지표 산출 (WAPE, RMSE, MAD)"""
    actual = np.array(actual, dtype=float)
    predicted = np.array(predicted, dtype=float)
    
    sum_actual = np.sum(actual)
    abs_errors = np.abs(actual - predicted)
    
    wape = (np.sum(abs_errors) / sum_actual * 100) if sum_actual > 0 else 0.0
    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mad = np.mean(abs_errors)
    
    return {
        "WAPE (%)": round(wape, 2),
        "RMSE": round(rmse, 3),
        "MAD": round(mad, 3)
    }

def calculate_dynamic_inventory_policy(part_row, weekly_demand_mean, weekly_demand_std, equip_failure_prob=0.0, gamma=0.8):
    """
    설비 예지보전(PdM) 연계 동적 안전재고(SS) 및 재주문점(ROP) 산출
    SS = z * sqrt(L * sigma_d^2 + d^2 * sigma_L^2) * (1 + gamma * P_failure)
    ROP = d * L + SS
    """
    # 리드타임을 주(week) 단위로 환산
    lead_time_days = float(part_row["lead_time_days"])
    lead_time_weeks = max(0.5, lead_time_days / 7.0)
    lead_time_std_weeks = float(part_row["lead_time_std"]) / 7.0
    
    service_level = float(part_row["target_service_level"])
    z_score = float(norm.ppf(service_level))
    
    d = max(0.05, float(weekly_demand_mean))
    sigma_d = max(0.05, float(weekly_demand_std))
    sigma_L = max(0.05, lead_time_std_weeks)
    
    # 1. 정적 안전재고 (Static Safety Stock)
    variance_term = lead_time_weeks * (sigma_d ** 2) + (d ** 2) * (sigma_L ** 2)
    static_ss = z_score * np.sqrt(max(0.01, variance_term))
    
    # 2. 설비 고장확률 연계 동적 안전재고 (Dynamic Safety Stock)
    pdm_factor = 1.0 + gamma * float(equip_failure_prob)
    dynamic_ss = static_ss * pdm_factor
    
    # 3. 재주문점 (ROP)
    ltd = d * lead_time_weeks  # Lead Time Demand
    static_rop = ltd + static_ss
    dynamic_rop = ltd + dynamic_ss
    
    # 정수 올림 처리
    ss_int = max(1, int(np.ceil(dynamic_ss)))
    rop_int = max(1, int(np.ceil(dynamic_rop)))
    
    current_stock = int(part_row["current_stock"])
    
    # 재고 상태 판정
    if current_stock <= rop_int:
        status = "🚨 긴급 발주 (Urgent)"
        order_qty_rec = max(2, int(np.ceil(rop_int * 1.5 - current_stock)))
    elif current_stock <= rop_int * 1.3:
        status = "⚠️ 주의 (Warning)"
        order_qty_rec = 0
    else:
        status = "✅ 적정 (Normal)"
        order_qty_rec = 0
        
    return {
        "lead_time_weeks": round(lead_time_weeks, 1),
        "lead_time_demand": round(ltd, 2),
        "static_ss": round(static_ss, 2),
        "dynamic_ss": ss_int,
        "static_rop": round(static_rop, 2),
        "dynamic_rop": rop_int,
        "current_stock": current_stock,
        "status": status,
        "recommended_order_qty": order_qty_rec
    }

def run_full_inventory_analysis(data_dir=DATA_DIR):
    """전체 부품에 대해 주차별 시계열 집계, 수요 예측 모델 평가, 동적 재고 정책 계산 수행"""
    # 1. 데이터 로드
    df_parts = pd.read_csv(os.path.join(data_dir, "part_master.csv"))
    df_equip = pd.read_csv(os.path.join(data_dir, "equipment_master.csv"))
    df_trans = pd.read_csv(os.path.join(data_dir, "part_transactions.csv"))
    
    df_trans["trans_date"] = pd.to_datetime(df_trans["trans_date"])
    df_trans["week"] = df_trans["trans_date"].dt.to_period("W").dt.start_time
    
    results = []
    
    # 각 부품별 분석
    for _, part in df_parts.iterrows():
        p_id = part["part_id"]
        
        # 주차별 수요량 집계
        part_trans = df_trans[df_trans["part_id"] == p_id]
        weekly_sum = part_trans.groupby("week")["qty_issued"].sum()
        
        # 최근 52주 타임라인 완성 (0값 보완)
        all_weeks = pd.date_range(end=df_trans["trans_date"].max(), periods=52, freq="W")
        weekly_series = weekly_sum.reindex(all_weeks, fill_value=0.0).values
        
        d_mean = np.mean(weekly_series)
        d_std = np.std(weekly_series)
        
        # 모델 예측값 산출
        sba_preds = sba_method(weekly_series, alpha=0.15)
        eval_metrics = evaluate_forecast(weekly_series, sba_preds)
        
        # 연결된 설비의 최고 고장확률 탐색 (가장 위험한 설비 기준)
        connected_equips = part_trans["equip_id"].unique()
        if len(connected_equips) > 0:
            equip_risks = df_equip[df_equip["equip_id"].isin(connected_equips)]["failure_prob"]
            max_failure_prob = equip_risks.max() if len(equip_risks) > 0 else 0.05
        else:
            max_failure_prob = 0.05
            
        policy = calculate_dynamic_inventory_policy(
            part, d_mean, d_std, equip_failure_prob=max_failure_prob, gamma=0.85
        )
        
        results.append({
            "part_id": p_id,
            "part_name": part["part_name"],
            "category": part["category"],
            "unit_cost": part["unit_cost_krw"],
            "abc_grade": part["abc_grade"],
            "ved_grade": part["ved_grade"],
            "weekly_demand_mean": round(d_mean, 2),
            "weekly_demand_std": round(d_std, 2),
            "sba_wape": eval_metrics["WAPE (%)"],
            "sba_rmse": eval_metrics["RMSE"],
            "current_stock": policy["current_stock"],
            "dynamic_ss": policy["dynamic_ss"],
            "dynamic_rop": policy["dynamic_rop"],
            "equip_failure_prob": round(max_failure_prob, 2),
            "status": policy["status"],
            "recommended_order_qty": policy["recommended_order_qty"]
        })
        
    df_results = pd.DataFrame(results)
    return df_results, df_parts, df_equip, df_trans

if __name__ == "__main__":
    print("[엔진 테스트] 재고 최적화 및 간헐적 수요 예측 실행 중...")
    df_res, _, _, _ = run_full_inventory_analysis()
    print(df_res[["part_id", "part_name", "current_stock", "dynamic_ss", "dynamic_rop", "status"]].head(10))
    print("\n[엔진 테스트 완료]")
