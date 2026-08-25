# 요양·실버시설 창업 입지/수요 분석 SaaS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Note on task style:** This is a data-analysis portfolio project, not a software feature. Coding tasks (parsing, region-code mapping, gap-index calculation) follow TDD with pytest as usual. Data-acquisition tasks (API 신청, 파일 다운로드) and the Tableau task are not unit-testable — their "test" step is a concrete verification action instead (row count check, screenshot check, etc). Do not skip those verification steps.

**Goal:** 국민건강보험공단·통계청 공공데이터를 결합해 시군구 단위 노인인구 대비 장기요양기관 정원의 수급 갭을 계산하고, Tableau 지도로 시각화해 예비 창업자용 입지 인사이트 리포트를 만든다.

**Architecture:** `collect → clean → analyze → visualize` 4단계 파이프라인. 각 단계는 `data/raw/` → `data/processed/` 사이를 이동하는 파일 기반 파이프라인이며, 단계 간 인터페이스는 CSV 스키마로 고정한다. 지표 계산 로직(수급 갭)은 순수 함수로 분리해 pytest로 검증한다.

**Tech Stack:** Python 3 (pandas, requests), SQLite 또는 CSV, pytest, Tableau Public/Desktop

**Spec:** `CLAUDE.md` (프로젝트 개요·데이터 소스·리스크), Notion 페이지(진행 로그)

## 제안 일정 (최소 1주, 2026-08-25 시작 기준)

| 일자 | 태스크 | 비고 |
|---|---|---|
| Day 1 (08-25, 오늘) | Task 1: 데이터 소스 확보 | 계정 가입·API 신청은 본인 로그인이 필요해 직접 진행. 승인 대기가 걸리면 이후 일정이 밀릴 수 있음 |
| Day 2 (08-26) | Task 2: 수집 파싱 | 승인 대기 중이어도 raw 파일 샘플만 있으면 착수 가능 |
| Day 3 (08-27) | Task 3: 지역코드 매핑 | |
| Day 4 (08-28) | Task 6: 실데이터 정제 (raw→clean) | 이 시점까지 실제 raw 컬럼명을 확인해둘 것 |
| Day 5 (08-29) | Task 4: 수급 갭 지표 계산 | |
| Day 6 (08-30, 주말) | Task 5: 파이프라인 조립 + 통합 테스트 | 태스크 2~4·6 산출물을 엔드투엔드로 연결 |
| Day 7 (08-31, 주말) | Task 7: Tableau 시각화 | 지도·필터·게시까지 |
| Day 8 (09-01, 여유일) | Task 8: 포트폴리오 리포트(README) | 버퍼 없이 7일에 다 못 끝냈을 때의 여유일 |

- 태스크당 하루 정도로 배분했지만, Task 1의 승인 대기 시간과 Task 7의 Tableau 숙련도에 따라 가장 밀리기 쉬움 — 이 두 태스크는 일정보다 늦어져도 순서를 바꾸지 말고 기다리는 대신 다음 태스크를 먼저 진행할 것.
- 매 태스크 완료 시 Notion 진행 로그에 날짜·완료 태스크·다음 태스크를 기록 (CLAUDE.md 규칙과 동일).

## Global Constraints

- 원본 데이터는 `data/raw/`, 정제본은 `data/processed/`에 저장하고 둘 다 `.gitignore`로 git 추적 제외 (폴더는 `.gitkeep`으로 유지)
- API 키/인증 정보는 `.env`에만 저장, `.env.example`만 커밋
- 공공데이터 사용 시 데이터셋별 공공누리 라이선스 유형을 확인하고 출처를 리포트에 명시
- 지역 단위는 시군구(시군구 코드 5자리, 통계청 행정구역코드 기준)로 통일 — 이후 모든 병합 키는 이 코드를 사용

---

### Task 1: 데이터 소스 확보 — 공공데이터포털/KOSIS 계정 및 원천 파일 확보

**Files:**
- Create: `.env.example`
- Create: `data/raw/.gitkeep`
- Create: `data/processed/.gitkeep`
- Modify: `.gitignore`

**Interfaces:**
- Produces: 아래 4개 원천 파일이 `data/raw/`에 존재
  - `data/raw/ltc_facilities_raw.csv` (국민건강보험공단 장기요양기관 시설별 현황)
  - `data/raw/elderly_population_raw.csv` (통계청 KOSIS 시군구별 65세 이상 인구)
  - `data/raw/ltc_grades_raw.csv` (복지로 장기요양기관 평가등급, 있으면)
  - `data/raw/region_codes.csv` (통계청 행정구역코드 마스터)

- [ ] **Step 1: 공공데이터포털(data.go.kr) 계정으로 아래 데이터셋 검색·다운로드/API 신청**
  - 국민건강보험공단_장기요양기관 시설별 현황
  - 없으면 노인장기요양보험 홈페이지(longtermcare.or.kr) 정보공개 메뉴에서 대체 파일 확보

- [ ] **Step 2: KOSIS(kosis.kr)에서 시군구별 65세 이상 인구 통계 다운로드**
  - KOSIS > 인구총조사 또는 주민등록인구현황 > 시군구별, 최신 연도 CSV 다운로드

- [ ] **Step 3: 통계청 행정구역코드(시군구 5자리) 마스터 파일 확보**
  - SGIS 또는 KOSIS 코드표에서 다운로드, 시도명·시군구명·코드 컬럼 포함 확인

- [ ] **Step 4: 위 파일들을 `data/raw/`에 저장하고 각 파일의 행 수·컬럼을 확인**

  Run: `python -c "import pandas as pd; [print(f, pd.read_csv(f, nrows=5).columns.tolist()) for f in ['data/raw/ltc_facilities_raw.csv','data/raw/elderly_population_raw.csv','data/raw/region_codes.csv']]"`

  Expected: 3개 파일 모두 에러 없이 컬럼 목록 출력 (인코딩은 `encoding='cp949'` 필요할 수 있음)

- [ ] **Step 5: `.env.example`, `.gitignore` 작성 및 커밋**

```
# .env.example
DATA_GO_KR_API_KEY=
```

```bash
git add .env.example .gitignore data/raw/.gitkeep data/processed/.gitkeep
git commit -m "chore: set up data directories and env template"
```

---

### Task 2: 수집 스크립트 — API 원본을 표준 CSV로 저장

**Files:**
- Create: `src/collect/fetch_ltc_facilities.py`
- Test: `tests/collect/test_fetch_ltc_facilities.py`

**Interfaces:**
- Consumes: `DATA_GO_KR_API_KEY` (환경변수), Task 1의 `data/raw/ltc_facilities_raw.csv`가 이미 수동 다운로드된 경우 이 스크립트는 파일 검증만 수행
- Produces: `parse_facility_rows(raw_json: dict) -> list[dict]` — 각 dict는 `{"region_code": str, "facility_type": str, "capacity": int, "current": int}` 키를 가짐

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/collect/test_fetch_ltc_facilities.py
from src.collect.fetch_ltc_facilities import parse_facility_rows

def test_parse_facility_rows_extracts_required_fields():
    raw_json = {
        "response": {
            "body": {
                "items": [
                    {"admCode": "11110", "svcTp": "노인요양시설", "cap": "50", "curNum": "42"}
                ]
            }
        }
    }
    result = parse_facility_rows(raw_json)
    assert result == [
        {"region_code": "11110", "facility_type": "노인요양시설", "capacity": 50, "current": 42}
    ]

def test_parse_facility_rows_handles_empty_items():
    raw_json = {"response": {"body": {"items": []}}}
    assert parse_facility_rows(raw_json) == []
```

- [ ] **Step 2: 테스트 실패 확인**

  Run: `pytest tests/collect/test_fetch_ltc_facilities.py -v`
  Expected: FAIL with `ModuleNotFoundError` or `ImportError` (함수 미정의)

- [ ] **Step 3: 최소 구현 작성**

```python
# src/collect/fetch_ltc_facilities.py
def parse_facility_rows(raw_json: dict) -> list[dict]:
    items = raw_json.get("response", {}).get("body", {}).get("items", [])
    return [
        {
            "region_code": item["admCode"],
            "facility_type": item["svcTp"],
            "capacity": int(item["cap"]),
            "current": int(item["curNum"]),
        }
        for item in items
    ]
```

  실제 API 응답 필드명(`admCode`, `svcTp`, `cap`, `curNum` 등)은 Task 1에서 받은 원본 파일/문서를 열어 실제 키 이름으로 교체할 것 — 위 이름은 플레이스홀더가 아니라 최초 추정치이며, 실데이터 확인 후 이 단계에서 바로 수정한다.

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/collect/test_fetch_ltc_facilities.py -v`
  Expected: PASS (2 passed)

- [ ] **Step 5: 커밋**

```bash
git add src/collect/fetch_ltc_facilities.py tests/collect/test_fetch_ltc_facilities.py
git commit -m "feat: parse LTC facility API response into flat rows"
```

---

### Task 3: 지역코드 정규화 — 시군구명을 5자리 코드로 매핑

**Files:**
- Create: `src/clean/region_mapper.py`
- Test: `tests/clean/test_region_mapper.py`

**Interfaces:**
- Consumes: `data/raw/region_codes.csv` (컬럼: `region_name`, `region_code`)
- Produces: `build_region_lookup(region_codes_path: str) -> dict[str, str]` (지역명 → 코드), `normalize_region_name(name: str) -> str` (공백/괄호 제거 등 표준화)

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/clean/test_region_mapper.py
import pandas as pd
from src.clean.region_mapper import normalize_region_name, build_region_lookup

def test_normalize_region_name_strips_whitespace_and_parens():
    assert normalize_region_name(" 수원시 장안구 (경기) ") == "수원시장안구"

def test_build_region_lookup_maps_name_to_code(tmp_path):
    csv_path = tmp_path / "region_codes.csv"
    pd.DataFrame(
        {"region_name": ["수원시 장안구"], "region_code": ["41111"]}
    ).to_csv(csv_path, index=False)

    lookup = build_region_lookup(str(csv_path))
    assert lookup["수원시장안구"] == "41111"
```

- [ ] **Step 2: 테스트 실패 확인**

  Run: `pytest tests/clean/test_region_mapper.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 최소 구현 작성**

```python
# src/clean/region_mapper.py
import re
import pandas as pd

def normalize_region_name(name: str) -> str:
    name = re.sub(r"\(.*?\)", "", name)
    return re.sub(r"\s+", "", name).strip()

def build_region_lookup(region_codes_path: str) -> dict[str, str]:
    df = pd.read_csv(region_codes_path, dtype=str)
    return {
        normalize_region_name(row["region_name"]): row["region_code"]
        for _, row in df.iterrows()
    }
```

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/clean/test_region_mapper.py -v`
  Expected: PASS (2 passed)

- [ ] **Step 5: 커밋**

```bash
git add src/clean/region_mapper.py tests/clean/test_region_mapper.py
git commit -m "feat: add region name normalization and code lookup"
```

---

### Task 4: 수급 갭 지표 계산 — 시군구별 인구 대비 정원 갭 산출

**Files:**
- Create: `src/analyze/gap_index.py`
- Test: `tests/analyze/test_gap_index.py`

**Interfaces:**
- Consumes: `facilities_df` (컬럼: `region_code`, `capacity`), `population_df` (컬럼: `region_code`, `elderly_population`)
- Produces: `compute_gap_index(facilities_df: pd.DataFrame, population_df: pd.DataFrame) -> pd.DataFrame` — 결과 컬럼: `region_code`, `total_capacity`, `elderly_population`, `capacity_per_1000_elderly`, `gap_rank` (값이 작을수록 공급 부족, 1이 가장 부족)

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/analyze/test_gap_index.py
import pandas as pd
from src.analyze.gap_index import compute_gap_index

def test_compute_gap_index_ranks_lower_supply_as_more_scarce():
    facilities_df = pd.DataFrame(
        {"region_code": ["A", "A", "B"], "capacity": [50, 50, 200]}
    )
    population_df = pd.DataFrame(
        {"region_code": ["A", "B"], "elderly_population": [10000, 10000]}
    )

    result = compute_gap_index(facilities_df, population_df)

    row_a = result[result["region_code"] == "A"].iloc[0]
    row_b = result[result["region_code"] == "B"].iloc[0]

    assert row_a["total_capacity"] == 100
    assert row_a["capacity_per_1000_elderly"] == 10.0
    assert row_b["capacity_per_1000_elderly"] == 20.0
    assert row_a["gap_rank"] == 1
    assert row_b["gap_rank"] == 2

def test_compute_gap_index_handles_region_with_zero_facilities():
    facilities_df = pd.DataFrame({"region_code": ["A"], "capacity": [50]})
    population_df = pd.DataFrame(
        {"region_code": ["A", "B"], "elderly_population": [10000, 5000]}
    )

    result = compute_gap_index(facilities_df, population_df)
    row_b = result[result["region_code"] == "B"].iloc[0]

    assert row_b["total_capacity"] == 0
    assert row_b["capacity_per_1000_elderly"] == 0.0
```

- [ ] **Step 2: 테스트 실패 확인**

  Run: `pytest tests/analyze/test_gap_index.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 최소 구현 작성**

```python
# src/analyze/gap_index.py
import pandas as pd

def compute_gap_index(facilities_df: pd.DataFrame, population_df: pd.DataFrame) -> pd.DataFrame:
    capacity_by_region = (
        facilities_df.groupby("region_code")["capacity"].sum().reset_index(name="total_capacity")
    )
    merged = population_df.merge(capacity_by_region, on="region_code", how="left")
    merged["total_capacity"] = merged["total_capacity"].fillna(0)
    merged["capacity_per_1000_elderly"] = (
        merged["total_capacity"] / merged["elderly_population"] * 1000
    )
    merged["gap_rank"] = merged["capacity_per_1000_elderly"].rank(method="min").astype(int)
    return merged
```

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/analyze/test_gap_index.py -v`
  Expected: PASS (2 passed)

- [ ] **Step 5: 커밋**

```bash
git add src/analyze/gap_index.py tests/analyze/test_gap_index.py
git commit -m "feat: compute per-region LTC capacity gap index"
```

---

### Task 5: 파이프라인 조립 — 원본 CSV부터 최종 지표 CSV까지 엔드투엔드 스크립트

**Files:**
- Create: `src/pipeline.py`
- Test: `tests/test_pipeline.py`

**Interfaces:**
- Consumes: Task 2의 `parse_facility_rows`, Task 3의 `build_region_lookup`/`normalize_region_name`, Task 4의 `compute_gap_index`
- Produces: `run_pipeline(raw_dir: str, processed_dir: str) -> str` — `data/processed/gap_index.csv` 경로를 반환

- [ ] **Step 1: 실패하는 테스트 작성 (임시 디렉토리에 최소 fixture 파일 생성 후 엔드투엔드 검증)**

```python
# tests/test_pipeline.py
import pandas as pd
from src.pipeline import run_pipeline

def test_run_pipeline_produces_gap_index_csv(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    pd.DataFrame(
        {"region_name": ["수원시 장안구"], "region_code": ["41111"]}
    ).to_csv(raw_dir / "region_codes.csv", index=False)

    pd.DataFrame(
        {"region_code": ["41111"], "capacity": [80]}
    ).to_csv(raw_dir / "ltc_facilities_clean.csv", index=False)

    pd.DataFrame(
        {"region_code": ["41111"], "elderly_population": [8000]}
    ).to_csv(raw_dir / "elderly_population_clean.csv", index=False)

    output_path = run_pipeline(str(raw_dir), str(processed_dir))
    result = pd.read_csv(output_path)

    assert (processed_dir / "gap_index.csv").exists()
    assert result.loc[0, "capacity_per_1000_elderly"] == 10.0
```

- [ ] **Step 2: 테스트 실패 확인**

  Run: `pytest tests/test_pipeline.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 최소 구현 작성**

```python
# src/pipeline.py
import os
import pandas as pd
from src.analyze.gap_index import compute_gap_index

def run_pipeline(raw_dir: str, processed_dir: str) -> str:
    facilities_df = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_clean.csv"))
    population_df = pd.read_csv(os.path.join(raw_dir, "elderly_population_clean.csv"))

    result = compute_gap_index(facilities_df, population_df)

    output_path = os.path.join(processed_dir, "gap_index.csv")
    result.to_csv(output_path, index=False)
    return output_path
```

  참고: 이 태스크에서는 `ltc_facilities_clean.csv`, `elderly_population_clean.csv`가 이미 지역코드로 정규화되어 있다고 가정한다. 원본 raw 파일(Task 1)을 이 형태로 정제하는 스크립트는 Task 3의 `region_mapper`를 사용해 별도로 작성해야 하며, 실제 원본 컬럼명을 확인한 뒤(Task 1 Step 4 결과 참고) `src/clean/` 아래에 `clean_facilities.py`, `clean_population.py`로 추가한다 — 원본 스키마를 봐야 정확한 컬럼 매핑을 정할 수 있으므로 이 태스크에서는 정규화 이후 형태만 계약으로 고정한다.

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/test_pipeline.py -v`
  Expected: PASS (1 passed)

- [ ] **Step 5: 커밋**

```bash
git add src/pipeline.py tests/test_pipeline.py
git commit -m "feat: assemble end-to-end pipeline producing gap index csv"
```

---

### Task 6: 실데이터 정제 스크립트 — raw → clean 컬럼 매핑 확정

**Files:**
- Create: `src/clean/clean_facilities.py`
- Create: `src/clean/clean_population.py`
- Test: `tests/clean/test_clean_facilities.py`
- Test: `tests/clean/test_clean_population.py`

**Interfaces:**
- Consumes: Task 1에서 받은 실제 raw CSV 컬럼명, Task 3의 `build_region_lookup`
- Produces: `clean_facilities(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame` (컬럼: `region_code`, `capacity`), `clean_population(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame` (컬럼: `region_code`, `elderly_population`)

- [ ] **Step 1: `data/raw/ltc_facilities_raw.csv`, `data/raw/elderly_population_raw.csv`를 열어 실제 컬럼명을 확인**

  Run: `python -c "import pandas as pd; print(pd.read_csv('data/raw/ltc_facilities_raw.csv', encoding='cp949', nrows=3))"`
  실제 지역명 컬럼, 정원 컬럼, 인구 컬럼 이름을 기록해둔다 (아래 테스트의 컬럼명을 여기서 확인한 실제 이름으로 교체할 것)

- [ ] **Step 2: 실패하는 테스트 작성 (Step 1에서 확인한 실제 컬럼명 사용)**

```python
# tests/clean/test_clean_facilities.py
import pandas as pd
from src.clean.clean_facilities import clean_facilities

def test_clean_facilities_maps_region_name_to_code_and_sums_capacity():
    raw_df = pd.DataFrame(
        {"시군구명": ["수원시 장안구", "수원시 장안구"], "정원": [30, 20]}
    )
    region_lookup = {"수원시장안구": "41111"}

    result = clean_facilities(raw_df, region_lookup)

    assert result.loc[0, "region_code"] == "41111"
    assert result.loc[0, "capacity"] == 50
```

  (컬럼명 `시군구명`, `정원`은 Step 1에서 확인한 실제 raw 컬럼명으로 반드시 교체)

- [ ] **Step 3: 테스트 실패 확인**

  Run: `pytest tests/clean/test_clean_facilities.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 4: 최소 구현 작성 (컬럼명은 Step 1 확인 결과 반영)**

```python
# src/clean/clean_facilities.py
import pandas as pd
from src.clean.region_mapper import normalize_region_name

def clean_facilities(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame:
    df = raw_df.copy()
    df["region_code"] = df["시군구명"].apply(normalize_region_name).map(region_lookup)
    df = df.dropna(subset=["region_code"])
    grouped = df.groupby("region_code")["정원"].sum().reset_index()
    return grouped.rename(columns={"정원": "capacity"})
```

- [ ] **Step 5: 테스트 통과 확인 후 `clean_population.py`도 동일한 패턴(Step 2~4)으로 반복 작성**

  Run: `pytest tests/clean/ -v`
  Expected: 모든 테스트 PASS

- [ ] **Step 6: 커밋**

```bash
git add src/clean/clean_facilities.py src/clean/clean_population.py tests/clean/
git commit -m "feat: clean raw facility and population data into pipeline schema"
```

---

### Task 7: Tableau 시각화 — 시군구 단위 수급 갭 지도

**Files:**
- Create: `outputs/figures/gap_index_preview.png` (Python 중간 확인용, Tableau 작업 전)
- Manual: Tableau 워크북 (`.twbx`는 리포지토리에 커밋하지 않음 — 개인 Tableau Public 계정에 게시)

**Interfaces:**
- Consumes: Task 5의 산출물 `data/processed/gap_index.csv`

- [ ] **Step 1: Python으로 지역별 `capacity_per_1000_elderly` 막대그래프를 빠르게 확인 (Tableau 작업 방향 판단용)**

```python
# 1회성 스크립트, notebooks/ 또는 셸에서 실행
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("data/processed/gap_index.csv").sort_values("capacity_per_1000_elderly")
df.plot.barh(x="region_code", y="capacity_per_1000_elderly", figsize=(8, 12))
plt.tight_layout()
plt.savefig("outputs/figures/gap_index_preview.png")
```

  Run 후 확인: `outputs/figures/gap_index_preview.png` 파일이 생성되고 지역별 값 분포가 육안으로 타당한지(음수 없음, 극단치 존재 여부) 확인

- [ ] **Step 2: Tableau에서 `data/processed/gap_index.csv`를 연결하고 시군구 경계 지도(SGIS Shapefile 또는 Tableau 내장 지역 매핑)에 `capacity_per_1000_elderly`를 색상으로 매핑**

- [ ] **Step 3: `gap_rank` 하위 10개 지역을 강조하는 필터/툴팁 추가**

- [ ] **Step 4: Tableau Public에 게시하고 URL을 Notion 진행 로그에 기록**

- [ ] **Step 5: 검증 — 게시된 대시보드를 열어 지도가 로드되고 툴팁이 정상 표시되는지 확인 후 스크린샷을 `outputs/figures/dashboard_screenshot.png`로 저장, 커밋**

```bash
git add outputs/figures/gap_index_preview.png outputs/figures/dashboard_screenshot.png
git commit -m "docs: add gap index preview chart and dashboard screenshot"
```

---

### Task 8: 포트폴리오 리포트 정리

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: 전체 파이프라인 산출물, Tableau 대시보드 URL, Notion 진행 로그

- [ ] **Step 1: README.md에 프로젝트 개요, 문제 인식, 데이터 소스, 파이프라인 구조, 핵심 발견(수급 갭 상위/하위 지역), Tableau 링크, AI(Claude Code) 협업 방식 요약을 작성**

- [ ] **Step 2: `pytest`를 전체 실행해 모든 테스트가 통과하는지 최종 확인**

  Run: `pytest -v`
  Expected: 전체 PASS

- [ ] **Step 3: 커밋**

```bash
git add README.md
git commit -m "docs: add portfolio README summarizing project and findings"
```
