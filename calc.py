from __future__ import annotations
from datetime import datetime, timedelta
from dateutil import parser
import pytz
import os
import pandas as pd

TZ = os.getenv("TZ", "Asia/Kolkata")
ZONE = pytz.timezone(TZ)

DATE_COL = "Date"        # change if your sheet uses different name
AMOUNT_COL = "Amount"    # default numeric metric

def _coerce_dates(df: pd.DataFrame) -> pd.DataFrame:
    if DATE_COL in df.columns:
        def try_parse(x):
            try:
                return parser.parse(str(x)).date()
            except Exception:
                return pd.NaT
        df = df.copy()
        df[DATE_COL] = df[DATE_COL].apply(try_parse)
    return df

def _date_range_for(timeframe: dict):
    today = datetime.now(ZONE).date()
    ttype = (timeframe or {}).get("type", "today")
    if ttype == "today":
        return today, today
    if ttype == "yesterday":
        y = today - timedelta(days=1)
        return y, y
    if ttype == "this_month":
        start = today.replace(day=1)
        # next month 1st minus 1 day
        end = (start.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        return start, end
    if ttype == "last_month":
        first_this = today.replace(day=1)
        end = first_this - timedelta(days=1)
        start = end.replace(day=1)
        return start, end
    if ttype == "last_7_days":
        return today - timedelta(days=6), today
    if ttype == "date_range":
        start = parser.parse(timeframe.get("start")).date()
        end = parser.parse(timeframe.get("end")).date()
        return start, end
    # default
    return today, today

def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    if not filters:
        return df
    out = df
    for k, v in filters.items():
        if k not in out.columns:
            # ignore silently if column missing
            continue
        # case-insensitive exact match on stringified values
        out = out[out[k].astype(str).str.lower() == str(v).lower()]
    return out

def _aggregate(df: pd.DataFrame, op: str, metric: str) -> float | int:
    if op == "count":
        return int(len(df))
    if metric not in df.columns:
        # gracefully fallback to count
        return int(len(df))
    series = pd.to_numeric(df[metric], errors="coerce")
    if op == "avg":
        return float(series.mean(skipna=True) or 0.0)
    # default sum
    return float(series.sum(skipna=True) or 0.0)

def _group_aggregate(df: pd.DataFrame, op: str, metric: str, group_cols: list[str]) -> pd.DataFrame:
    if not group_cols:
        total = _aggregate(df, op, metric)
        return pd.DataFrame({"group": ["ALL"], "value": [total]})
    tmp = df.copy()
    if metric in tmp.columns:
        tmp[metric] = pd.to_numeric(tmp[metric], errors="coerce")
    else:
        # if metric missing and op=count, we can still group
        tmp[metric] = 1
        op = "sum" if op != "count" else "sum"
    if op == "avg":
        agg = tmp.groupby(group_cols, dropna=False)[metric].mean(numeric_only=True).reset_index()
    elif op == "count":
        agg = tmp.groupby(group_cols, dropna=False).size().reset_index(name="value")
        return agg.rename(columns={"size": "value"})
    else:
        agg = tmp.groupby(group_cols, dropna=False)[metric].sum(numeric_only=True).reset_index()
    if "value" not in agg.columns:
        agg = agg.rename(columns={metric: "value"})
    return agg

def run_query(df: pd.DataFrame, intent: dict) -> list[str]:
    """Return a list of response lines for WhatsApp."""
    df = _coerce_dates(df)

    # timeframe filter
    start, end = _date_range_for(intent.get("timeframe", {}))
    if DATE_COL in df.columns:
        mask = (df[DATE_COL] >= start) & (df[DATE_COL] <= end)
        df = df[mask]

    # column filters
    df = _apply_filters(df, intent.get("filters", {}))

    op = intent.get("operation", "sum")
    metric = intent.get("metric", AMOUNT_COL)
    group_by = intent.get("group_by", []) or []
    top_k = intent.get("top_k")

    # aggregation
    if group_by:
        agg = _group_aggregate(df, op, metric, group_by)
        # sort by value descending
        if "value" in agg.columns:
            agg = agg.sort_values("value", ascending=False)
        if top_k and isinstance(top_k, int) and top_k > 0:
            agg = agg.head(top_k)
        lines = []
        lines.append(f"✅ {op.upper()} of {metric} from {start} to {end}:")
        for _, row in agg.iterrows():
            grp_vals = [str(row.get(col, '')) for col in group_by]
            label = " | ".join(grp_vals)
            val = row.get("value", 0)
            if isinstance(val, float):
                val = round(val, 2)
            lines.append(f"- {label}: {val}")
        if len(lines) == 1:
            lines.append("No matching rows.")
        return lines
    else:
        total = _aggregate(df, op, metric)
        if isinstance(total, float):
            total = round(total, 2)
        return [f"✅ {op.upper()} of {metric} from {start} to {end}: {total}"]
