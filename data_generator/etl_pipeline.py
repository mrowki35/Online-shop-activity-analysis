from pyspark.sql.functions import *
from pyspark.sql.types import *
import os

# 1. Pobranie zmiennych z klastra (skonfigurowanych przez Terraform)
eh_conn_str = os.environ.get("EVENT_HUB_CONN_STR")
eh_name = os.environ.get("EVENT_HUB_NAME")
storage_name = os.environ.get("STORAGE_ACCOUNT_NAME")
storage_key = os.environ.get("STORAGE_ACCOUNT_KEY")

# 2. Konfiguracja połączenia do Event Hub
# Musimy dodać EntityPath do connection stringa, jeśli go tam nie ma
connectionString = f"{eh_conn_str};EntityPath={eh_name}"
conf = {
  'eventhubs.connectionString' : sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(connectionString)
}

# 3. Odczyt strumienia z Event Hub
df = spark.readStream \
  .format("eventhubs") \
  .options(**conf) \
  .load()

# 4. Parsowanie danych (zakładając, że wysyłasz JSONy)
# Body w Event Hub jest binarny, więc musimy go rzutować na String
stream_df = df.withColumn("body", col("body").cast("string"))

# 5. Konfiguracja uprawnień do zapisu w Storage Account
spark.conf.set(f"fs.azure.account.key.{storage_name}.dfs.core.windows.net", storage_key)

# 6. ZAPIS danych do folderu 'data' (format Delta)
checkpoint_path = f"abfss://data@{storage_name}.dfs.core.windows.net/checkpoints/etl_pipeline"
output_path = f"abfss://data@{storage_name}.dfs.core.windows.net/raw_clickstream"

query = stream_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", checkpoint_path) \
    .start(output_path)