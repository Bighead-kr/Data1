# 요양·실버시설 창업 입지/수요 분석 SaaS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Note on task style:** This is a data-analysis portfolio project, not a software feature. Coding tasks (parsing, region-code mapping, gap-index calculation) follow TDD with pytest as usual. Data-acquisition tasks (API 신청, 파일 다운로드) and the Tableau task are not unit-testable — their "test" step is a concrete verification action instead (row count check, screenshot check, etc). Do not skip those verification steps.

**Goal:** 국민건강보험공단·통계청 공공데이터를 결합해 시군구 단위 노인인구 대비 장기요양기관 정원의 수급 갭을 계산하고, Tableau 지도로 시각화해 예비 창업자용 입지 인사이트 리포트를 만든다.

**Architecture:** `collect → clean → analyze → visualize` 4단계 파이프라인. 각 단계는 `data/raw/` → `data/processed/` 사이를 이동하는 파일 기반 파이프라인이며, 단계 간 인터페이스는 CSV 스키마로 고정한다. 지표 계산 로직(수급 갭)은 순수 함수로 분리해 pytest로 검증한다.

**Tech Stack:** Python 3 (pandas, openpyxl), CSV 파일 기반 파이프라인, pytest, Tableau Public/Desktop

**Spec:** `CLAUDE.md` (프로젝트 개요·데이터 소스·리스크), Notion 페이지(진행 로그)

## 제안 일정 (최소 1주, 2026-08-25 시작 기준)

| 일자 | 태스크 | 비고 |
|---|---|---|
| Day 1 (08-25, 오늘) | Task 1: 데이터 소스 확보 | [완료] 원본 파일 6종 수동 확보 + CSV 변환까지 끝남. API 신청 절차 자체가 불필요해져 일정이 하루 앞당겨짐 |
| Day 2 (08-26) | Task 2: 원본 로더/스키마 검증 | API 파싱이 아니라 로컬 CSV 스키마 검증으로 범위 축소됨 |
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
- **[2026-08-25 확정] 지역 결합 키는 숫자 코드가 아니라 "시도명+시군구명" 텍스트 정규화 키를 사용한다.** 건강보험공단 파일의 `시군구코드`(예: 종로구=110)와 통계청 코드표의 5자리 코드(종로구=11010)가 서로 다른 체계라 숫자 join이 틀린 지역에 매칭된다. 최종 산출물의 `region_code` 컬럼값 자체는 통계청 5자리 코드를 쓰되, 그 코드를 찾는 매칭 과정은 반드시 이름 기반으로 한다.
- **[알려진 리스크] 광주/전남 통합 이슈:** 인구 통계 원본에 "전남광주통합특별시"라는 명칭이 등장하는데, 통계청 행정구역 코드표(`region_codes_raw.csv`, 2024년 기준)에는 이 명칭이 없을 수 있다. Task 6에서 이름 매칭이 안 되는 지역이 있으면 누락 처리하지 말고 반드시 원인을 확인하고 수동 매핑 예외 처리를 추가할 것.

---

### Task 1: 데이터 소스 확보 — 원천 파일 확보 및 CSV 정리 [완료 2026-08-25]

**Files:**
- Create: `.gitignore`
- Create: `data/raw/.gitkeep`
- Create: `data/processed/.gitkeep`

**Interfaces:**
- Produces: 아래 6개 원천 CSV가 `data/raw/`에 존재 (API 신청 없이 수동 다운로드 + xlsx→CSV 변환으로 확보 완료)
  - `data/raw/ltc_facilities_general.csv` (30,595행) — 컬럼: `장기요양기관코드, 장기요양기관이름, 우편번호, 시도코드, 시군구코드, 법정동코드, 시도 시군구 법정동명, 지정일자, 설치신고일자, 기관별 상세주소`
  - `data/raw/ltc_facilities_capacity.csv` (43,581행) — 컬럼: `장기요양기관코드, 기관유형코드, 기관유형명, 정원`
  - `data/raw/ltc_facilities_staffing.csv` (49,162행) — 이번 스코프(수급 갭 지표)에서는 미사용, 심화 분석용으로 보관
  - `data/raw/ltc_facility_type_codes.csv` (35행) — 컬럼: `코드, 이름` (A01~C06 등 기관유형 코드표)
  - `data/raw/region_codes_raw.csv` (3,841행) — 컬럼: `code, name`, 2자리(시도)/5자리(시군구)/8자리(읍면동) 계층형 통계청 행정구역코드
  - `data/raw/인구총조사_고령인구비율_시도_시_군_구__20260825134933.csv` (248행) — 컬럼: `행정구역별(1)(시도), 행정구역별(2)(시군구), 행정구역별(3), 2025(고령인구비율%), 2025.1(65세이상인구), 2025.2(전체인구)`. **주의: 1행(index 0)은 진짜 데이터가 아니라 두 번째 헤더 행이 데이터처럼 읽힌 것 — 반드시 스킵할 것**

- [x] **Step 1: 국민건강보험공단 장기요양기관 시설별 현황 xlsx 확보 (수동 다운로드, 사용자 제공)**

- [x] **Step 2: 통계청 65세 이상 인구 CSV(KOSIS) 확보 (수동 다운로드, 사용자 제공)**

- [x] **Step 3: 통계청 행정구역코드 마스터 xlsx 확보 (수동 다운로드, 사용자 제공)**

- [x] **Step 4: xlsx 파일들을 시트별 CSV로 변환 (openpyxl 설치 후 pandas로 변환)**

  실행한 변환:
  ```python
  import pandas as pd
  xl = pd.ExcelFile('data/raw/국민건강보험공단_장기요양기관 시설별 현황_20260610.xlsx')
  name_map = {
      '일반현황': 'ltc_facilities_general.csv',
      '입소인원': 'ltc_facilities_capacity.csv',
      '인력현황': 'ltc_facilities_staffing.csv',
      '기관유형코드 정의': 'ltc_facility_type_codes.csv',
  }
  for sheet, fname in name_map.items():
      xl.parse(sheet).to_csv(f'data/raw/{fname}', index=False, encoding='utf-8-sig')
  ```
  결과 확인: 5개 CSV 모두 정상 생성, 행 수는 위 Interfaces 목록과 일치

- [x] **Step 5: 원본 xlsx 삭제, CSV만 유지**

  Run: `ls data/raw/`
  Expected: `.xlsx` 파일 없이 CSV 5종 + `.gitkeep`만 존재 — 확인 완료

- [ ] **Step 6: `.gitignore` 작성 및 커밋**

```
# .gitignore (추가)
data/raw/*
data/processed/*
!data/raw/.gitkeep
!data/processed/.gitkeep
.env
```

```bash
git add .gitignore data/raw/.gitkeep data/processed/.gitkeep
git commit -m "chore: set up data directories and gitignore for raw/processed data"
```

---

### Task 2: 원본 CSV 로더 및 스키마 검증 — API 호출 없이 파일 기반 수집 계층

**Files:**
- Create: `src/collect/load_raw.py`
- Test: `tests/collect/test_load_raw.py`

**Interfaces:**
- Consumes: Task 1의 `data/raw/*.csv` 5종
- Produces:
  - `REQUIRED_COLUMNS: dict[str, list[str]]` — 파일명 → 필수 컬럼 목록 상수
  - `load_and_validate(path: str, required_columns: list[str]) -> pd.DataFrame` — 필수 컬럼이 없으면 `ValueError` 발생, 있으면 그대로 반환

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/collect/test_load_raw.py
import pandas as pd
import pytest
from src.collect.load_raw import load_and_validate

def test_load_and_validate_returns_dataframe_when_columns_present(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1], "b": [2]}).to_csv(csv_path, index=False)

    result = load_and_validate(str(csv_path), required_columns=["a", "b"])

    assert list(result.columns) == ["a", "b"]
    assert len(result) == 1

def test_load_and_validate_raises_when_required_column_missing(tmp_path):
    csv_path = tmp_path / "sample.csv"
    pd.DataFrame({"a": [1]}).to_csv(csv_path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_and_validate(str(csv_path), required_columns=["a", "b"])
```

- [ ] **Step 2: 테스트 실패 확인**

  Run: `pytest tests/collect/test_load_raw.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 최소 구현 작성**

```python
# src/collect/load_raw.py
import pandas as pd

REQUIRED_COLUMNS = {
    "ltc_facilities_general.csv": [
        "장기요양기관코드", "시도 시군구 법정동명",
    ],
    "ltc_facilities_capacity.csv": [
        "장기요양기관코드", "기관유형코드", "정원",
    ],
    "region_codes_raw.csv": ["code", "name"],
}

def load_and_validate(path: str, required_columns: list[str]) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"missing required columns: {missing}")
    return df
```

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/collect/test_load_raw.py -v`
  Expected: PASS (2 passed)

- [ ] **Step 5: 실제 raw 파일에 대해 수동으로 스모크 테스트**

  Run:
  ```bash
  python -c "
  from src.collect.load_raw import load_and_validate, REQUIRED_COLUMNS
  for fname, cols in REQUIRED_COLUMNS.items():
      df = load_and_validate(f'data/raw/{fname}', cols)
      print(fname, df.shape)
  "
  ```
  Expected: 3개 파일 모두 에러 없이 `(행수, 컬럼수)` 출력

- [ ] **Step 6: 커밋**

```bash
git add src/collect/load_raw.py tests/collect/test_load_raw.py
git commit -m "feat: add raw CSV loader with required-column validation"
```

---

### Task 3: 지역코드 정규화 — "시도명+시군구명" 텍스트 키를 5자리 코드로 매핑

**배경:** `region_codes_raw.csv`는 계층형 목록이라 5자리(시군구) 행에는 시군구명만 있고 시도명은 없다 (예: `11010, 종로구`). 시도명은 그 상위 2자리 행(`11, 서울특별시`)에만 있다. 코드의 앞 2자리가 부모 시도 코드와 같다는 성질을 이용해 "시도명+시군구명" 결합 키를 만들어야, 여러 시도에 동명 시군구가 있는 경우(중구, 서구 등)도 구분할 수 있다.

**Files:**
- Create: `src/clean/region_mapper.py`
- Test: `tests/clean/test_region_mapper.py`

**Interfaces:**
- Consumes: `data/raw/region_codes_raw.csv` (컬럼: `code`, `name`, 2/5/8자리 계층형)
- Produces:
  - `normalize_region_name(name: str) -> str` — 공백/괄호 제거
  - `combine_region_key(sido: str, sigungu: str) -> str` — 정규화된 시도명+시군구명 결합 키
  - `build_region_lookup(region_codes_path: str) -> dict[str, str]` — 결합 키 → 5자리 코드

- [ ] **Step 1: 실패하는 테스트 작성**

```python
# tests/clean/test_region_mapper.py
import pandas as pd
from src.clean.region_mapper import (
    normalize_region_name,
    combine_region_key,
    build_region_lookup,
)

def test_normalize_region_name_strips_whitespace_and_parens():
    assert normalize_region_name(" 장안구 (경기) ") == "장안구"

def test_combine_region_key_joins_normalized_parts():
    assert combine_region_key("경기도", " 수원시 장안구 ") == "경기도수원시장안구"

def test_build_region_lookup_uses_parent_sido_code_prefix(tmp_path):
    csv_path = tmp_path / "region_codes_raw.csv"
    pd.DataFrame(
        {
            "code": ["11", "11010", "11020", "41", "41111"],
            "name": ["서울특별시", "종로구", "중구", "경기도", "수원시장안구"],
        }
    ).to_csv(csv_path, index=False)

    lookup = build_region_lookup(str(csv_path))

    assert lookup["서울특별시종로구"] == "11010"
    assert lookup["서울특별시중구"] == "11020"
    assert lookup["경기도수원시장안구"] == "41111"
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
    name = re.sub(r"\(.*?\)", "", str(name))
    return re.sub(r"\s+", "", name).strip()

def combine_region_key(sido: str, sigungu: str) -> str:
    return normalize_region_name(sido) + normalize_region_name(sigungu)

def build_region_lookup(region_codes_path: str) -> dict[str, str]:
    df = pd.read_csv(region_codes_path, dtype=str)
    df["code_len"] = df["code"].str.len()

    sido_names = dict(zip(df.loc[df["code_len"] == 2, "code"], df.loc[df["code_len"] == 2, "name"]))

    lookup = {}
    for _, row in df.loc[df["code_len"] == 5].iterrows():
        sido_code = row["code"][:2]
        sido_name = sido_names.get(sido_code)
        if sido_name is None:
            continue
        key = combine_region_key(sido_name, row["name"])
        lookup[key] = row["code"]
    return lookup
```

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/clean/test_region_mapper.py -v`
  Expected: PASS (3 passed)

- [ ] **Step 5: 실제 `region_codes_raw.csv`로 스모크 테스트 — 264개 시군구 전부 매핑되는지 확인**

  Run:
  ```bash
  python -c "
  from src.clean.region_mapper import build_region_lookup
  lookup = build_region_lookup('data/raw/region_codes_raw.csv')
  print('mapped regions:', len(lookup))
  "
  ```
  Expected: `mapped regions: 264` (Global Constraints의 5자리 코드 개수와 일치해야 함 — 다르면 원인을 조사할 것, 세종특별자치시처럼 5자리 코드 없이 2자리로만 존재하는 특수 케이스가 있을 수 있음)

- [ ] **Step 6: 커밋**

```bash
git add src/clean/region_mapper.py tests/clean/test_region_mapper.py
git commit -m "feat: build sido+sigungu combined key to 5-digit region code lookup"
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
- Consumes: Task 6의 `clean_facilities`/`clean_population`, Task 4의 `compute_gap_index`
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

  참고: 이 태스크의 테스트는 이미 지역코드로 정규화된 `ltc_facilities_clean.csv`, `elderly_population_clean.csv` fixture로 검증한다. 실제 raw → 이 형태로의 정제는 Task 6의 `clean_facilities`/`clean_population`이 담당하며, `run_pipeline`은 그 함수들을 호출하도록 아래처럼 구현한다.

```python
# src/pipeline.py (실제 raw 파일 기준 최종 버전)
import os
import pandas as pd
from src.clean.region_mapper import build_region_lookup
from src.clean.clean_facilities import clean_facilities
from src.clean.clean_population import clean_population
from src.analyze.gap_index import compute_gap_index

def run_pipeline(raw_dir: str, processed_dir: str) -> str:
    region_lookup = build_region_lookup(os.path.join(raw_dir, "region_codes_raw.csv"))
    general = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_general.csv"), dtype=str)
    capacity = pd.read_csv(os.path.join(raw_dir, "ltc_facilities_capacity.csv"), dtype=str)
    pop_raw = pd.read_csv(
        os.path.join(raw_dir, "인구총조사_고령인구비율_시도_시_군_구__20260825134933.csv"), dtype=str
    )

    facilities_df = clean_facilities(general, capacity, region_lookup)
    population_df = clean_population(pop_raw, region_lookup)

    result = compute_gap_index(facilities_df, population_df)

    output_path = os.path.join(processed_dir, "gap_index.csv")
    result.to_csv(output_path, index=False)
    return output_path
```

  아래 Step 3의 최소 구현(fixture 기반 clean CSV를 직접 읽는 버전)으로 먼저 테스트를 통과시킨 뒤, 이 실제 버전으로 교체한다 — 교체 후에는 `tests/test_pipeline.py`의 fixture도 raw 스키마(`ltc_facilities_general.csv` 등 실제 파일명)에 맞게 다시 써야 한다.

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

**배경 (2026-08-25 실데이터 확인 결과):**
- `ltc_facilities_general.csv`의 `시도 시군구 법정동명` 컬럼은 `"서울특별시 종로구 구기동"`처럼 시도·시군구·법정동이 공백으로 이어진 한 문자열이다. 앞의 두 토큰만 잘라내면 시도명·시군구명이 된다.
- `ltc_facilities_capacity.csv`의 `정원`은 기관유형코드에 따라 의미가 다르다. 입소시설(`A01, A02, A03, A04, A05, AAA`)만 "시설 수용 정원"이고, `B*/C*`(재가서비스: 방문요양·방문목욕 등)는 다른 개념이라 이번 수급 갭 지표에서 제외한다 (사용자 확인 완료).
- 인구 CSV(`인구총조사_고령인구비율_...csv`)는 헤더가 2줄이라 pandas가 1번째 데이터 행을 헤더 잔재로 잘못 읽는다 — 반드시 skip. 또한 `행정구역별(2)`가 `"소계"`인 행은 시도 전체 합계(시군구 아님)라 제외해야 하는데, 세종특별자치시는 시군구 구분이 없어 소계 행이 곧 유일한 데이터 행이다 — 이 경우만 예외로 유지한다.

**Files:**
- Create: `src/clean/clean_facilities.py`
- Create: `src/clean/clean_population.py`
- Test: `tests/clean/test_clean_facilities.py`
- Test: `tests/clean/test_clean_population.py`

**Interfaces:**
- Consumes: Task 3의 `build_region_lookup`, `combine_region_key`
- Produces:
  - `INSTITUTIONAL_TYPE_CODES: set[str]` = `{"A01", "A02", "A03", "A04", "A05", "AAA"}`
  - `extract_sido_sigungu(full_name: str) -> tuple[str, str]` — `"서울특별시 종로구 구기동"` → `("서울특별시", "종로구")`
  - `clean_facilities(general_df: pd.DataFrame, capacity_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame` (컬럼: `region_code`, `capacity`)
  - `clean_population(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame` (컬럼: `region_code`, `elderly_population`)

- [ ] **Step 1: 실패하는 테스트 작성 — `clean_facilities`**

```python
# tests/clean/test_clean_facilities.py
import pandas as pd
from src.clean.clean_facilities import extract_sido_sigungu, clean_facilities

def test_extract_sido_sigungu_takes_first_two_tokens():
    assert extract_sido_sigungu("서울특별시 종로구 구기동") == ("서울특별시", "종로구")

def test_clean_facilities_filters_non_institutional_types_and_sums_capacity():
    general_df = pd.DataFrame(
        {
            "장기요양기관코드": ["F1", "F1", "F2"],
            "시도 시군구 법정동명": [
                "서울특별시 종로구 구기동",
                "서울특별시 종로구 구기동",
                "서울특별시 종로구 평창동",
            ],
        }
    ).drop_duplicates(subset=["장기요양기관코드"])
    capacity_df = pd.DataFrame(
        {
            "장기요양기관코드": ["F1", "F2", "F2"],
            "기관유형코드": ["A03", "A03", "B01"],
            "정원": [30, 20, 999],
        }
    )
    region_lookup = {"서울특별시종로구": "11010"}

    result = clean_facilities(general_df, capacity_df, region_lookup)
    row = result[result["region_code"] == "11010"].iloc[0]

    assert row["capacity"] == 50  # B01(재가서비스) 999는 제외되어야 함
```

- [ ] **Step 2: 테스트 실패 확인**

  Run: `pytest tests/clean/test_clean_facilities.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: 최소 구현 작성**

```python
# src/clean/clean_facilities.py
import pandas as pd
from src.clean.region_mapper import combine_region_key

INSTITUTIONAL_TYPE_CODES = {"A01", "A02", "A03", "A04", "A05", "AAA"}

def extract_sido_sigungu(full_name: str) -> tuple[str, str]:
    tokens = str(full_name).split()
    return tokens[0], tokens[1]

def clean_facilities(
    general_df: pd.DataFrame, capacity_df: pd.DataFrame, region_lookup: dict
) -> pd.DataFrame:
    general = general_df.drop_duplicates(subset=["장기요양기관코드"]).copy()
    general[["sido", "sigungu"]] = general["시도 시군구 법정동명"].apply(
        lambda s: pd.Series(extract_sido_sigungu(s))
    )
    general["region_code"] = general.apply(
        lambda r: region_lookup.get(combine_region_key(r["sido"], r["sigungu"])), axis=1
    )

    institutional = capacity_df[capacity_df["기관유형코드"].isin(INSTITUTIONAL_TYPE_CODES)].copy()
    institutional["정원"] = institutional["정원"].astype(int)

    merged = institutional.merge(
        general[["장기요양기관코드", "region_code"]], on="장기요양기관코드", how="left"
    )
    merged = merged.dropna(subset=["region_code"])

    grouped = merged.groupby("region_code")["정원"].sum().reset_index()
    return grouped.rename(columns={"정원": "capacity"})
```

- [ ] **Step 4: 테스트 통과 확인**

  Run: `pytest tests/clean/test_clean_facilities.py -v`
  Expected: PASS (2 passed)

- [ ] **Step 5: 실패하는 테스트 작성 — `clean_population`**

```python
# tests/clean/test_clean_population.py
import pandas as pd
from src.clean.clean_population import clean_population

def test_clean_population_drops_summary_rows_and_maps_region_code():
    raw_df = pd.DataFrame(
        {
            "행정구역별(1)": ["행정구역별(1)", "전국", "서울특별시", "서울특별시", "세종특별자치시"],
            "행정구역별(2)": ["행정구역별(2)", "소계", "소계", "종로구", "소계"],
            "2025.1": ["65세이상인구 (명)", "10722557", "1881288", "29432", "50000"],
        }
    )
    region_lookup = {"서울특별시종로구": "11010", "세종특별자치시세종특별자치시": "36110"}

    result = clean_population(raw_df, region_lookup)

    assert set(result["region_code"]) == {"11010", "36110"}
    row = result[result["region_code"] == "11010"].iloc[0]
    assert row["elderly_population"] == 29432
```

  (세종특별자치시는 시군구 구분이 없어 `combine_region_key(시도명, 시도명)`으로 자기 자신을 시군구처럼 취급 — `build_region_lookup`이 세종을 5자리 코드로 못 찾으면 Task 3 Step 5에서 발견되었을 별도 예외 매핑을 여기서 사용한다)

- [ ] **Step 6: 테스트 실패 확인**

  Run: `pytest tests/clean/test_clean_population.py -v`
  Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 7: 최소 구현 작성**

```python
# src/clean/clean_population.py
import pandas as pd
from src.clean.region_mapper import combine_region_key

def clean_population(raw_df: pd.DataFrame, region_lookup: dict) -> pd.DataFrame:
    df = raw_df.iloc[1:].copy()  # 1행은 헤더 잔재라 스킵
    df = df[
        (df["행정구역별(2)"] != "소계") | (df["행정구역별(1)"] == "세종특별자치시")
    ].copy()
    df["sigungu"] = df.apply(
        lambda r: r["행정구역별(1)"] if r["행정구역별(1)"] == "세종특별자치시" else r["행정구역별(2)"],
        axis=1,
    )
    df["region_code"] = df.apply(
        lambda r: region_lookup.get(combine_region_key(r["행정구역별(1)"], r["sigungu"])), axis=1
    )
    df = df.dropna(subset=["region_code"])
    df["elderly_population"] = df["2025.1"].astype(int)
    return df[["region_code", "elderly_population"]].reset_index(drop=True)
```

- [ ] **Step 8: 테스트 통과 확인**

  Run: `pytest tests/clean/test_clean_population.py -v`
  Expected: PASS (1 passed)

- [ ] **Step 9: 실제 raw 파일 전체로 스모크 테스트 — 매칭 안 되는 지역이 있는지 확인**

  Run:
  ```bash
  python -c "
  import pandas as pd
  from src.clean.region_mapper import build_region_lookup
  from src.clean.clean_facilities import clean_facilities
  from src.clean.clean_population import clean_population

  lookup = build_region_lookup('data/raw/region_codes_raw.csv')
  general = pd.read_csv('data/raw/ltc_facilities_general.csv', dtype=str)
  capacity = pd.read_csv('data/raw/ltc_facilities_capacity.csv', dtype=str)
  pop_raw = pd.read_csv('data/raw/인구총조사_고령인구비율_시도_시_군_구__20260825134933.csv', dtype=str)

  fac = clean_facilities(general, capacity, lookup)
  pop = clean_population(pop_raw, lookup)
  print('facilities regions matched:', fac.shape)
  print('population regions matched:', pop.shape)
  print('population rows with no region_code:', pop_raw.iloc[1:].shape[0] - pop.shape[0])
  "
  ```
  Expected: 두 결과 모두 비어있지 않고, 매칭 안 된 인구 행 수가 0에 가까워야 함 (전남/광주 통합 이슈 등으로 남으면 Global Constraints에 적어둔 리스크대로 원인 확인 후 예외 매핑 추가)

- [ ] **Step 10: 커밋**

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
