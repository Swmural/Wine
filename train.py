import random
import sys
import numpy as np

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, DoubleType
from pyspark.sql.functions import col, desc
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import MultilayerPerceptronClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator



spark = SparkSession.builder.appName("WineQualityPrediction").master("local").getOrCreate()
spark.sparkContext.setLogLevel("Error")
# spark.conf.set("spark.hadoop.fs.s3a.access.key", "ASIA2AD65DTPZUQCGXY3")
# spark.conf.set("spark.hadoop.fs.s3a.secret.key", "97cbDLjKsZFUpj6dpBwsk54aiXqamr47OevwUZjD")

# Load the training dataset
df = spark.read.option("delimiter", ";").csv("s3://wimequalitypredictiondataset/TrainingDataset.csv", header=True, inferSchema=True)

# df = spark.read.format("csv").load("s3://wimequalitypredictiondataset/TrainingDataset.csv", header=True, sep=";")


df = df.toDF("fixed_acidity", "volatile_acidity", "citric_acid", "residual_sugar", "chlorides", "free_sulfur_dioxide", "total_sulfur_dioxide", "density", "pH", "sulphates", "alcohol", "label")



df = df \
        .withColumn("fixed_acidity", col("fixed_acidity").cast(DoubleType())) \
        .withColumn("volatile_acidity", col("volatile_acidity").cast(DoubleType())) \
        .withColumn("citric_acid", col("citric_acid").cast(DoubleType())) \
        .withColumn("residual_sugar", col("residual_sugar").cast(DoubleType())) \
        .withColumn("chlorides", col("chlorides").cast(DoubleType())) \
        .withColumn("free_sulfur_dioxide", col("free_sulfur_dioxide").cast(IntegerType())) \
        .withColumn("total_sulfur_dioxide", col("total_sulfur_dioxide").cast(IntegerType())) \
        .withColumn("density", col("density").cast(DoubleType())) \
        .withColumn("pH", col("pH").cast(DoubleType())) \
        .withColumn("sulphates", col("sulphates").cast(DoubleType())) \
        .withColumn("alcohol", col("alcohol").cast(DoubleType())) \
        .withColumn("label", col("label").cast(IntegerType()))


features = df.columns
features = features[:-1]


va = VectorAssembler(inputCols=features, outputCol="features")
df_va = va.transform(df)
df_va = df_va.select(["features", "label"])
df = df_va


layers = [11, 8, 8, 8, 8, 10]


train1 = MultilayerPerceptronClassifier(maxIter=1000, layers=layers, blockSize=64, stepSize=0.04, solver='l-bfgs')

Model = train1.fit(df)

local_model_path = "file:///home/ec2-user/best_model_lr"

# Save the model to the local file system
Model.write().overwrite().save(local_model_path)

print(f"Model Created and saved to {local_model_path}.")
