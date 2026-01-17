import os

from pyspark.sql.functions import *
from pyspark.sql.types import *

eh_conn_str = os.environ.get("EVENT_HUB_CONN_STR")
eh_name = os.environ.get("EVENT_HUB_NAME")
storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
storage_key = os.environ.get("STORAGE_ACCOUNT_KEY")

connectionString = f"{eh_conn_str};EntityPath={eh_name}"
conf = {
    "eventhubs.connectionString": sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
        connectionString
    )
}

df = spark.readStream.format("eventhubs").options(**conf).load()


stream_df = df.withColumn("body", col("body").cast("string"))

spark.conf.set(f"fs.azure.account.key.{storage_name}.dfs.core.windows.net", storage_key)

checkpoint_path = (
    f"abfss://data@{storage_name}.dfs.core.windows.net/checkpoints/etl_pipeline"
)
output_path = f"abfss://data@{storage_name}.dfs.core.windows.net/raw_clickstream"

query = (
    stream_df.writeStream.format("delta")
    .outputMode("append")
    .option("checkpointLocation", checkpoint_path)
    .start(output_path)
)
