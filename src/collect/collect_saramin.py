"""사람인 채용 공고 수집 스크립트.

사용 예:
    python src/collect/collect_saramin.py --keywords "데이터 분석가" --keywords "데이터 엔지니어"
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.collect.saramin_client import SaraminAPIError, SaraminClient

RAW_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "saramin"


def collect(keywords: list[str]) -> None:
    client = SaraminClient()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for keyword in keywords:
        jobs = list(client.search_all(keyword))
        out_path = RAW_DIR / f"{keyword.replace(' ', '_')}_{timestamp}.json"
        out_path.write_text(
            json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[{keyword}] {len(jobs)}건 수집 -> {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--keywords",
        action="append",
        required=True,
        help="검색할 직무 키워드 (여러 번 지정 가능)",
    )
    args = parser.parse_args()

    try:
        collect(args.keywords)
    except SaraminAPIError as e:
        print(f"오류: {e}", file=sys.stderr)
        sys.exit(1)
