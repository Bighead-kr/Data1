import pandas as pd
import numpy as np

def compute_gap_index(facilities_df: pd.DataFrame, population_df: pd.DataFrame) -> pd.DataFrame:
    capacity_by_region = (
        facilities_df.groupby("region_code")["capacity"].sum().reset_index(name="total_capacity")
    )
    merged = population_df.merge(capacity_by_region, on="region_code", how="left")
    merged["total_capacity"] = merged["total_capacity"].fillna(0)
    merged["capacity_per_1000_elderly"] = np.where(
        merged["elderly_population"] > 0,
        merged["total_capacity"] / merged["elderly_population"] * 1000,
        0.0,
    )
    merged["gap_rank"] = merged["capacity_per_1000_elderly"].rank(method="min").astype(int)
    return merged
