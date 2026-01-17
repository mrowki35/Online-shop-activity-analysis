# COMMAND ----------
from pyspark.sql.functions import *
from pyspark.sql.types import *

df = spark.read.table("gold_session_stats")

# COMMAND ----------
display(df)

# COMMAND ----------
kpi_df = df.select(
    count("*").alias("total_sessions"),
    sum("is_purchased").alias("total_orders"),
    sum("is_abandoned_cart").alias("total_abandoned"),
    round(sum("session_revenue"), 2).alias("total_revenue"),
    round(avg("session_revenue"), 2).alias("avg_order_value"),
)

display(kpi_df)

# COMMAND ----------
status_df = df.withColumn(
    "session_status",
    when(col("is_purchased") == 1, "Purchased")
    .when(col("is_abandoned_cart") == 1, "Abandoned Cart")
    .otherwise("Browsing Only"),
)

display(status_df.groupBy("session_status").count())

# COMMAND ----------
timeline_df = (
    df.groupBy(window(col("window_start"), "1 hour").alias("time_window"))
    .agg(
        count("*").alias("sessions"),
        sum("is_abandoned_cart").alias("abandoned_count"),
        sum("is_purchased").alias("purchases_count"),
    )
    .orderBy("time_window")
)

display(timeline_df)

# COMMAND ----------
revenue_df = (
    df.filter(col("session_revenue") > 0)
    .select("userId", "session_revenue", "window_start")
    .orderBy(col("window_start").desc())
)

display(revenue_df)

# COMMAND ----------
conversion_df = (
    df.select(lit("All Sessions").alias("step"), count("*").alias("count"))
    .union(
        df.filter(col("is_abandoned_cart") == 1).select(
            lit("Cart Activity").alias("step"), count("*").alias("count")
        )
    )
    .union(
        df.filter(col("is_purchased") == 1).select(
            lit("Purchased").alias("step"), count("*").alias("count")
        )
    )
)

display(conversion_df)

# COMMAND ----------
top_users_df = (
    df.groupBy("userId")
    .agg(
        sum("session_revenue").alias("lifetime_value"),
        count("*").alias("total_sessions"),
        sum("is_purchased").alias("total_purchases"),
    )
    .orderBy(col("lifetime_value").desc())
    .limit(10)
)

display(top_users_df)
