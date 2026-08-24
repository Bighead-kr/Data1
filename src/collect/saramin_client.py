"""사람인 오픈 API(oapi.saramin.co.kr) 클라이언트."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://oapi.saramin.co.kr/job-search"


class SaraminAPIError(RuntimeError):
    pass


class SaraminClient:
    def __init__(self, access_key: str | None = None):
        self.access_key = access_key or os.getenv("SARAMIN_API_KEY")
        if not self.access_key:
            raise SaraminAPIError(
                "SARAMIN_API_KEY가 설정되어 있지 않습니다. .env 파일을 확인하세요."
            )

    def search_jobs(
        self,
        keywords: str,
        start: int = 1,
        count: int = 100,
        fields: str = "posting-date,expiration-date,industry,job-category,job-type,education-level",
        **extra_params,
    ) -> dict:
        """채용 공고를 검색한다. count는 최대 110까지 허용된다."""
        params = {
            "access-key": self.access_key,
            "keywords": keywords,
            "start": start,
            "count": count,
            "fields": fields,
            "format": "json",
            **extra_params,
        }
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if "jobs" not in data:
            raise SaraminAPIError(f"예상치 못한 응답 형식: {data}")
        return data

    def search_all(self, keywords: str, page_size: int = 100, max_pages: int = 50, **extra_params):
        """전체 페이지를 순회하며 공고 목록(dict)을 하나씩 yield한다."""
        start = 1
        for _ in range(max_pages):
            data = self.search_jobs(keywords, start=start, count=page_size, **extra_params)
            jobs = data["jobs"].get("job", [])
            if isinstance(jobs, dict):
                jobs = [jobs]
            if not jobs:
                break
            yield from jobs
            if len(jobs) < page_size:
                break
            start += page_size
