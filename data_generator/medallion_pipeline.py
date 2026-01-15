# COMMAND ----------
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os

eh_conn_str = os.environ.get("EVENT_HUB_CONN_STR")
eh_name = os.environ.get("EVENT_HUB_NAME")
storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
storage_key = os.environ.get("STORAGE_ACCOUNT_KEY")

spark.conf.set(f"fs.azure.account.key.{storage_name}.dfs.core.windows.net", storage_key)
base_path = f"abfss://data@{storage_name}.dfs.core.windows.net"

# COMMAND ----------
connectionString = f"{eh_conn_str};EntityPath={eh_name}"
ehConf = {
  'eventhubs.connectionString' : sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(connectionString)
}

raw_stream_df = spark.readStream \
  .format("eventhubs") \
  .options(**ehConf) \
  .load()

bronze_query = raw_stream_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", f"{base_path}/checkpoints/bronze") \
    .table("bronze_clickstream")

# COMMAND ----------
json_schema = StructType([
    StructField("eventId", StringType(), True),
    StructField("eventType", StringType(), True),
    StructField("timestamp", TimestampType(), True),
    StructField("userId", StringType(), True),
    StructField("sessionId", StringType(), True),
    StructField("pageUrl", StringType(), True),
    StructField("device", StructType([
        StructField("type", StringType(), True),
        StructField("os", StringType(), True),
        StructField("ip", StringType(), True)
    ]), True),
    StructField("data", StructType([
        StructField("productId", StringType(), True),
        StructField("productName", StringType(), True),
        StructField("price", DoubleType(), True),
        StructField("currency", StringType(), True),
        StructField("searchQuery", StringType(), True),
        StructField("totalAmount", DoubleType(), True)
    ]), True)
])

bronze_df = spark.readStream.table("bronze_clickstream")

silver_df = bronze_df \
    .select(from_json(col("body").cast("string"), json_schema).alias("parsed")) \
    .select("parsed.*") \
    .withColumn("event_time", col("timestamp").cast("timestamp")) \
    .withColumn("total_amount", col("data.totalAmount")) \
    .withWatermark("event_time", "10 minutes") \
    .dropDuplicates(["eventId", "event_time"])

silver_query = silver_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", f"{base_path}/checkpoints/silver") \
    .table("silver_clickstream")

# COMMAND ----------
silver_stream = spark.readStream.table("silver_clickstream")

gold_df = silver_stream \
    .groupBy(
        col("userId"), 
        session_window(col("event_time"), "30 minutes").alias("session_window")
    ) \
    .agg(
        count("*").alias("events_count"),
        max(when(col("eventType") == "PURCHASE", 1).otherwise(0)).alias("is_purchased"),
        max(when(col("eventType") == "ADD_TO_CART", 1).otherwise(0)).alias("has_cart_activity"),
        sum(col("total_amount")).alias("session_revenue"),
        min("event_time").alias("session_start"),
        max("event_time").alias("session_end")
    ) \
    .select(
        col("userId"),
        col("session_window.start").alias("window_start"),
        col("session_window.end").alias("window_end"),
        col("events_count"),
        col("is_purchased"),
        col("session_revenue"),
        when((col("has_cart_activity") == 1) & (col("is_purchased") == 0), 1)
        .otherwise(0).alias("is_abandoned_cart")
    )

gold_query = gold_df.writeStream \
    .format("delta") \
    .outputMode("complete") \
    .option("checkpointLocation", f"{base_path}/checkpoints/gold") \
    .table("gold_session_stats")