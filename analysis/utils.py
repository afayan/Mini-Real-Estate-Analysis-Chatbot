import pandas as pd
from django.conf import settings

_df_cache = None


AREA_COL = "final_location"
PRICE_COL = "flat_-_weighted_average_rate"     
DEMAND_COL = "flat_sold_-_igr"                 
UNITS_COL = "total_units"
CARPET_COL = "total_carpet_area_supplied_(sqft)"


def get_dataset():
    global _df_cache
    if _df_cache is None:
        df = pd.read_excel(settings.REAL_ESTATE_FILE)
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        _df_cache = df
    
    return _df_cache


def detect_areas_from_query(query: str):
    df = get_dataset()

    if AREA_COL not in df.columns:
        return []

    all_areas = df[AREA_COL].dropna().unique()
    q = query.lower()
    matched = []

    for area in all_areas:
        if str(area).lower() in q:
            matched.append(str(area))

   
    seen = set()
    unique = []
    for a in matched:
        if a not in seen:
            seen.add(a)
            unique.append(a)

    return unique


def build_analysis(query: str):
    df = get_dataset()
    areas = detect_areas_from_query(query)

    if not areas:
        return {
            "summary": "I could not detect any known locality in your query. Please type a locality that exists in the 'final location' column of the dataset, for example: Akurdi, Ambegaon Budruk, Aundh, or Wakad.",
            "chartData": [],
            "tableData": [],
            "areas": [],
        }

    if AREA_COL not in df.columns or "year" not in df.columns:
        return {
            "summary": "The dataset is missing expected columns like 'final location' or 'year'.",
            "chartData": [],
            "tableData": [],
            "areas": areas,
        }

    filtered = df[df[AREA_COL].isin(areas)].copy()

   
    agg_kwargs = {}
    if PRICE_COL in filtered.columns:
        agg_kwargs["avg_price"] = (PRICE_COL, "mean")
    if DEMAND_COL in filtered.columns:
        agg_kwargs["total_demand"] = (DEMAND_COL, "sum")

    chart_rows = (
        filtered.groupby(["year", AREA_COL])
        .agg(**agg_kwargs)
        .reset_index()
        .sort_values(["year", AREA_COL])
    )

    chart_data = []
    for _, row in chart_rows.iterrows():
        item = {
            "year": int(row["year"]),
            "area": row[AREA_COL],
        }
        if "avg_price" in row:
            item["avg_price"] = float(row["avg_price"])
        if "total_demand" in row:
            item["avg_demand"] = float(row["total_demand"])
        chart_data.append(item)

   
    table_cols = [col for col in [
        "year",
        AREA_COL,
        PRICE_COL if PRICE_COL in filtered.columns else None,
        DEMAND_COL if DEMAND_COL in filtered.columns else None,
        UNITS_COL if UNITS_COL in filtered.columns else None,
        CARPET_COL if CARPET_COL in filtered.columns else None,
    ] if col is not None]

    table_data = filtered[table_cols].head(200).to_dict(orient="records")

  
    summaries = []
    for area in areas:
        area_df = filtered[filtered[AREA_COL] == area]
        if area_df.empty:
            continue

        min_year = int(area_df["year"].min())
        max_year = int(area_df["year"].max())

        part = f"For {area}, between {min_year} and {max_year}, "

        if PRICE_COL in area_df.columns:
            first_price = area_df[area_df["year"] == min_year][PRICE_COL].mean()
            last_price = area_df[area_df["year"] == max_year][PRICE_COL].mean()
            if pd.notna(first_price) and pd.notna(last_price):
                trend = "increased" if last_price > first_price else "decreased"
                part += f"the flat weighted average rate has {trend} from about {first_price:,.0f} to {last_price:,.0f}. "

        if DEMAND_COL in area_df.columns:
            total_demand = area_df[DEMAND_COL].sum()
            part += f"Total flat sales recorded in this period are roughly {total_demand:,.0f} units. "

        summaries.append(part.strip())

    if summaries:
        summary_text = (
            "Here is a quick snapshot based on the uploaded dataset. "
            + " ".join(summaries)
        )
    else:
        summary_text = "I could not compute a detailed summary for the selected localities."

    return {
        "summary": summary_text,
        "chartData": chart_data,
        "tableData": table_data,
        "areas": areas,
    }
