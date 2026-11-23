# 스마트팩토리 AI 프로젝트 (코디세이 조별과제)

이노베이션 아카데미 코디세이(Codyssey) 스마트팩토리 도메인 조별과제 리포지토리입니다.

## 🎯 확정 프로젝트 주제
**설비 예지보전(PdM) 연계 스마트팩토리 스페어파트(Spare Parts) 지능형 재고관리 및 발주 최적화 시스템**
- **핵심 목표**: 설비 IoT 건전도 센서 지표와 간헐적(Zero-inflated) 시계열 수요 예측을 융합하여, 과잉 재고 비용을 대폭 절감하고 치명적인 다운타임 결품을 사전에 방지
- **주요 기술**: ABC-VED 다차원 부품 분류, Croston's Method / SBA, 동적 안전재고(Dynamic SS) 및 재주문점(Dynamic ROP), Streamlit 5-Tab 웹 관제 대시보드
- **UI/UX 특장점**: 버튼 하나로 **라이트(☀️) / 그레이(🏢) / 다크(🌙) 모드** 실시간 순환 전환 지원 (HTML 가이드, 슬라이드, 대시보드 전체 적용)
- **비주얼 그래픽**: 자율 스마트팩토리 운영 조감도(`images/smart_factory_hero.png`), 4단계 파이프라인 아키텍처(`images/architecture_diagram.png`), 4분할 분석 인포그래픽(`images/spare_parts_analytics_dashboard.png`) 수록

---

## ⚡ 빠른 실행 가이드 (Quick Start)
```bash
# 1. 4대 테이블 모의 데이터셋 및 SQLite DB 생성 (20개 부품, 8개 설비, 687건 출고, 102건 발주)
py -3.9 generate_dataset.py

# 2. 간헐적 수요 예측 및 동적 ROP 최적화 엔진 검증
py -3.9 forecast_engine.py

# 3. Streamlit 웹 관제 대시보드 실행 (브라우저에서 localhost:8501 접속)
py -3.9 -m streamlit run app.py
```

---

## 📌 3대 프로젝트 가이드 및 발표 문서 (자동 동기화 유지)
- 📽️ **프레젠테이션 슬라이드 (HTML)**: [smart_factory_slides.html](file:///g:/내%20드라이브/aiworks/20261123_smartfactory/smart_factory_slides.html) *(방향키, F 전체화면, T 테마전환 지원)*
- 🌐 **웹 브라우저 가이드 (HTML)**: [smart_factory_project_guide.html](file:///g:/내%20드라이브/aiworks/20261123_smartfactory/smart_factory_project_guide.html) (또는 [index.html](file:///g:/내%20드라이브/aiworks/20261123_smartfactory/index.html))
- 📝 **마크다운 종합 가이드 (MD)**: [smart_factory_project_guide.md](file:///g:/내%20드라이브/aiworks/20261123_smartfactory/smart_factory_project_guide.md)
