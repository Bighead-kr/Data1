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
