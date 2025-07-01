import os
import logging
import pandas as pd
import functions_framework
from flask import jsonify, make_response

# ——— Logger setup ———
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s"
    ))
    logger.addHandler(h)

@functions_framework.cloud_event
def gcs_trigger_process(cloud_event):
    """
    Triggered by a GCS finalize (object create) event.
    Only processes CSVs under the 'raw_data/' prefix.
    """
    data = cloud_event.data
    bucket = data.get("bucket")
    name = data.get("name")

    # 1 Filter by folder & extension
    if not name.startswith("raw_data/"):
        logger.info("Skipping object not in raw_data/: %s", name)
        return make_response(("Ignored non-raw_data path", 204))
    if not name.lower().endswith(".csv"):
        logger.warning("Skipping non-CSV object: %s", name)
        return make_response(("Ignored non-CSV file", 204))

    # 2 Build GCS URI and read
    uri = f"gs://{bucket}/{name}"
    try:
        logger.info("Reading CSV from %s", uri)
        df = pd.read_csv(uri)
    except Exception as e:
        logger.error("Failed to read CSV %s: %s", uri, e, exc_info=True)
        return make_response((f"Error reading CSV: {e}", 500))

    # 3 Log a sample and count
    logger.info("Data sample:\n%s", df.head().to_string())
    record_count = len(df)
    logger.info("Total records read from %s: %d", name, record_count)

    # 4 Return JSON with count
    return make_response(jsonify({"record_count": record_count}), 200)