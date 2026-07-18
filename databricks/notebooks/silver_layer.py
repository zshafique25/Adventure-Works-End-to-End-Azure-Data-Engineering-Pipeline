# Databricks notebook source
# MAGIC %md
# MAGIC # SILVER LAYER SCRIPT

# COMMAND ----------

from pyspark.sql.functions import *
from pyspark.sql.types import *
from great_expectations.dataset import SparkDFDataset

# COMMAND ----------

# MAGIC %md
# MAGIC ### PARAMETERS
# MAGIC Set from the notebook UI when run manually, or passed as Base Parameters when triggered from an ADF Notebook activity.

# COMMAND ----------

dbutils.widgets.text("storage_account", "awstoragedatalakezain")
dbutils.widgets.text("secret_scope", "aw-project-scope")

storage_account = dbutils.widgets.get("storage_account")
secret_scope = dbutils.widgets.get("secret_scope")

# COMMAND ----------

# MAGIC %md
# MAGIC ### DATA ACCESS USING APPLICATION
# MAGIC Credentials are pulled from a Databricks secret scope — nothing is hardcoded in this notebook.
# MAGIC
# MAGIC One-time setup (Databricks CLI), and do this with a **freshly rotated** client secret since the old one was previously hardcoded in plaintext:
# MAGIC ```
# MAGIC databricks secrets create-scope aw-project-scope
# MAGIC databricks secrets put-secret aw-project-scope entra-client-id
# MAGIC databricks secrets put-secret aw-project-scope entra-client-secret
# MAGIC databricks secrets put-secret aw-project-scope entra-tenant-id
# MAGIC ```

# COMMAND ----------

client_id = dbutils.secrets.get(secret_scope, "entra-client-id")
client_secret = dbutils.secrets.get(secret_scope, "entra-client-secret")
tenant_id = dbutils.secrets.get(secret_scope, "entra-tenant-id")

spark.conf.set(f"fs.azure.account.auth.type.{storage_account}.dfs.core.windows.net", "OAuth")
spark.conf.set(f"fs.azure.account.oauth.provider.type.{storage_account}.dfs.core.windows.net", "org.apache.hadoop.fs.azurebfs.oauth2.ClientCredsTokenProvider")
spark.conf.set(f"fs.azure.account.oauth2.client.id.{storage_account}.dfs.core.windows.net", client_id)
spark.conf.set(f"fs.azure.account.oauth2.client.secret.{storage_account}.dfs.core.windows.net", client_secret)
spark.conf.set(f"fs.azure.account.oauth2.client.endpoint.{storage_account}.dfs.core.windows.net", f"https://login.microsoftonline.com/{tenant_id}/oauth2/token")

# COMMAND ----------

# MAGIC %md
# MAGIC ### HELPER FUNCTIONS

# COMMAND ----------

def validate_dataframe(df, table_name, column_checks=None):
    """
    Run Great Expectations checks on a Bronze dataframe before it's transformed/written.
    Raises an exception on failure, which fails the notebook run and (when orchestrated
    from ADF) blocks any downstream activity on the pipeline's Success path.
    """
    ge_df = SparkDFDataset(df)
    checks = [ge_df.expect_table_row_count_to_be_between(min_value=1)]

    if column_checks:
        for col_name in column_checks:
            checks.append(ge_df.expect_column_values_to_not_be_null(col_name))

    failed = [c for c in checks if not c["success"]]
    if failed:
        failed_types = [c["expectation_config"]["expectation_type"] for c in failed]
        raise Exception(f"Data quality check(s) failed for {table_name}: {failed_types}")

    print(f"\u2713 {table_name}: {len(checks)} quality check(s) passed")


def write_silver(df, table_name, mode="overwrite"):
    """Write a dataframe to the Silver container in Delta format."""
    df.write.format("delta") \
        .mode(mode) \
        .option("path", f"abfss://silver@{storage_account}.dfs.core.windows.net/{table_name}") \
        .save()
    print(f"\u2713 Wrote {table_name} to Silver (Delta, mode={mode})")

# COMMAND ----------

# MAGIC %md
# MAGIC ### DATA LOADING

# COMMAND ----------

# MAGIC %md
# MAGIC #### Reading Data

# COMMAND ----------

df_cal = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Calendar')

df_cus = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Customers')

df_procat = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Product_Categories')

df_pro = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Products')

df_ret = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Returns')

df_sales = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Sales*')

df_ter = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Territories')

df_subcat = spark.read.format('csv')\
            .option("header", True)\
            .option("inferSchema", True)\
            .load(f'abfss://bronze@{storage_account}.dfs.core.windows.net/AdventureWorks_Product_Subcategories')

# COMMAND ----------

# MAGIC %md
# MAGIC ### TRANSFORMATIONS

# COMMAND ----------

# MAGIC %md
# MAGIC #### Calendar

# COMMAND ----------

df_cal = df_cal.withColumn('Month', month(col('Date')))\
            .withColumn('Year', year(col('Date')))

# COMMAND ----------

validate_dataframe(df_cal, "Calendar", column_checks=["Date"])

# COMMAND ----------

write_silver(df_cal, "AdventureWorks_Calendar")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Customers

# COMMAND ----------

df_cus = df_cus.withColumn("fullname", concat_ws(" ", col("Prefix"), col("FirstName"), col("LastName")))

# COMMAND ----------

validate_dataframe(df_cus, "Customers")

# COMMAND ----------

write_silver(df_cus, "AdventureWorks_Customers")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Sub categories

# COMMAND ----------

validate_dataframe(df_subcat, "Product Subcategories")

# COMMAND ----------

write_silver(df_subcat, "AdventureWorks_Product_Subcategories")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Products

# COMMAND ----------

df_pro = df_pro.withColumn("ProductSKU", split(col("ProductSKU"), "-")[0])\
               .withColumn("ProductName", split(col("ProductName"), " ")[0])

# COMMAND ----------

validate_dataframe(df_pro, "Products")

# COMMAND ----------

write_silver(df_pro, "AdventureWorks_Products")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Returns

# COMMAND ----------

validate_dataframe(df_ret, "Returns")

# COMMAND ----------

write_silver(df_ret, "AdventureWorks_Returns")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Territories

# COMMAND ----------

validate_dataframe(df_ter, "Territories")

# COMMAND ----------

write_silver(df_ter, "AdventureWorks_Territories")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Product Categories

# COMMAND ----------

validate_dataframe(df_procat, "Product Categories")

# COMMAND ----------

write_silver(df_procat, "AdventureWorks_Product_Categories")

# COMMAND ----------

# MAGIC %md
# MAGIC #### Sales

# COMMAND ----------

df_sales = df_sales.withColumn("StockDate", to_timestamp(col("StockDate")))\
                  .withColumn("OrderNumber", regexp_replace(col("OrderNumber"), "S", "T"))\
                  .withColumn("Multiply", col("OrderLineItem") * col("OrderQuantity"))

# COMMAND ----------

validate_dataframe(df_sales, "Sales", column_checks=["OrderNumber", "OrderDate"])

# COMMAND ----------

write_silver(df_sales, "AdventureWorks_Sales")