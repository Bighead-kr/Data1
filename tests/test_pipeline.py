import pandas as pd

from src.pipeline import run_pipeline


def _write_fixtures(raw_dir):
    # region_codes_raw.csv: 2자리 시도코드 + 5자리 시군구코드 계층 구조.
    (raw_dir / "region_codes_raw.csv").write_text(
        "code,name\n"
        "11,서울특별시\n"
        "11010,종로구\n"
        "26,부산광역시\n"
        "26110,중구\n",
        encoding="utf-8",
    )

    # ltc_facilities_general.csv: 실제 원본과 동일한 컬럼명(장기요양기관코드, 시도 시군구 법정동명).
    (raw_dir / "ltc_facilities_general.csv").write_text(
        "장기요양기관코드,시도 시군구 법정동명\n"
        "A0001,서울특별시 종로구 구기동\n"
        "A0002,서울특별시 종로구 평창동\n",
        encoding="utf-8",
    )

    # ltc_facilities_capacity.csv: 기관유형코드가 시설(A03)인 것만 정원에 합산되어야 함.
    (raw_dir / "ltc_facilities_capacity.csv").write_text(
        "장기요양기관코드,기관유형코드,정원\n"
        "A0001,A03,30\n"
        "A0002,A03,50\n",
        encoding="utf-8",
    )

    # 인구총조사 CSV: 실제 원본과 동일한 "2025" 3중 컬럼 + 1행 헤더 잔재 구조.
    (raw_dir / "인구총조사_고령인구비율_시도_시_군_구__20260825134933.csv").write_text(
        "행정구역별(1),행정구역별(2),행정구역별(3),2025,2025,2025\n"
        "행정구역별(1),행정구역별(2),행정구역별(3),고령인구비율 (%),65세이상인구 (명),전체인구 (명)\n"
        "서울특별시,종로구,소계,20.6,8000,143114\n"
        "부산광역시,중구,소계,18.0,4000,50000\n",
        encoding="utf-8",
    )


def test_run_pipeline_produces_gap_index_csv(tmp_path):
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"
    raw_dir.mkdir()
    processed_dir.mkdir()

    _write_fixtures(raw_dir)

    output_path = run_pipeline(str(raw_dir), str(processed_dir))
    # region_code는 선행 0이 없는 자릿수 코드지만 의미상 문자열 식별자이므로
    # CSV 재로드 시 dtype을 명시해 int 추론에 의한 값 변형을 방지한다.
    result = pd.read_csv(output_path, dtype={"region_code": str})

    assert (processed_dir / "gap_index.csv").exists()

    seoul_jongno = result[result["region_code"] == "11010"].iloc[0]
    assert seoul_jongno["total_capacity"] == 80
    assert seoul_jongno["elderly_population"] == 8000
    assert seoul_jongno["capacity_per_1000_elderly"] == 10.0
    assert seoul_jongno["region_name"] == "서울특별시 종로구"

    # 부산 중구는 시설 데이터가 전혀 없는 지역 -> capacity 0으로 채워져야 함.
    busan_jung = result[result["region_code"] == "26110"].iloc[0]
    assert busan_jung["total_capacity"] == 0
    assert busan_jung["capacity_per_1000_elderly"] == 0.0

    # 공급이 적은 지역(부산 중구)이 더 시급하므로 gap_rank가 더 낮아야 함.
    assert busan_jung["gap_rank"] < seoul_jongno["gap_rank"]
