"""
Apache Spark Session Factory Module
Initializes and configures SparkSession with JVM modularity flags and memory management.
"""

import os
import sys
from pathlib import Path
from pyspark.sql import SparkSession
from src.config import APP_NAME, SPARK_MASTER, SPARK_DRIVER_MEMORY


def setup_pyspark_environment():
    """Ensure worker processes and JVM options are configured properly on Windows."""
    # Ensure current python executable is used for PySpark worker processes
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

    # Check and set JAVA_HOME if unset
    if "JAVA_HOME" not in os.environ:
        default_java = Path("C:/Program Files/Java/jdk-21")
        if default_java.exists():
            os.environ["JAVA_HOME"] = str(default_java)


def get_spark_session(app_name: str = APP_NAME, master: str = SPARK_MASTER) -> SparkSession:
    """
    Creates or retrieves an existing SparkSession configured for local distributed processing.
    
    Includes JVM open-module flags required for Java 17 and Java 21 LTS runtimes.
    """
    setup_pyspark_environment()

    jvm_flags = (
        "--add-opens=java.base/java.lang=ALL-UNNAMED "
        "--add-opens=java.base/java.lang.invoke=ALL-UNNAMED "
        "--add-opens=java.base/java.lang.reflect=ALL-UNNAMED "
        "--add-opens=java.base/java.io=ALL-UNNAMED "
        "--add-opens=java.base/java.net=ALL-UNNAMED "
        "--add-opens=java.base/java.nio=ALL-UNNAMED "
        "--add-opens=java.base/java.util=ALL-UNNAMED "
        "--add-opens=java.base/java.util.concurrent=ALL-UNNAMED "
        "--add-opens=java.base/java.util.concurrent.atomic=ALL-UNNAMED "
        "--add-opens=java.base/sun.nio.ch=ALL-UNNAMED "
        "--add-opens=java.base/sun.nio.cs=ALL-UNNAMED "
        "--add-opens=java.base/sun.security.action=ALL-UNNAMED "
        "--add-opens=java.base/sun.util.calendar=ALL-UNNAMED"
    )

    builder = (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.driver.memory", SPARK_DRIVER_MEMORY)
        .config("spark.sql.shuffle.partitions", "8")
        .config("spark.driver.extraJavaOptions", jvm_flags)
        .config("spark.executor.extraJavaOptions", jvm_flags)
        .config("spark.ui.enabled", "false")  # Disables UI port binding overhead during batch scripts
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
    )

    spark = builder.getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    return spark


def stop_spark_session(spark: SparkSession):
    """Safely shuts down the SparkSession."""
    if spark:
        spark.stop()
