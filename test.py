import random
import sys

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, DoubleType
from pyspark.sql.functions import col, desc
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import MultilayerPerceptronClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator


spark = SparkSession.builder.appName("test").master("local").getOrCreate()
spark.sparkContext.setLogLevel("Error")


df = spark.read.format("csv").load("s3://wimequalitypredictiondataset/ValidationDataset.csv", header=True, sep=";")

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

local_model_path = "/home/ec2-user/best_model_lr"

Model =  MultilayerPerceptronClassificationModel.load(f"file://{local_model_path}")

output = Model.transform(df)

evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
accevaluator = evaluator.evaluate(output)
print("############################")
print("Accuracy : %g " % accevaluator)
print("############################")
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
f1evaluator = evaluator.evaluate(output)
print("############################")
print("F1-score : %g " % f1evaluator)
print("############################")
