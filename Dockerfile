# Use CentOS 7 as base image
FROM centos:7

# Update and install necessary packages
RUN yum -y update && yum -y install python3 python3-dev python3-pip python3-virtualenv \
    java-1.8.0-openjdk wget

# Check Python versions
RUN python -V
RUN python3 -V

# Set environment variables for PySpark
ENV PYSPARK_DRIVER_PYTHON python3
ENV PYSPARK_PYTHON python3

# Upgrade pip and install required Python packages
RUN pip3 install --upgrade pip
RUN pip3 install numpy pandas

# Install Apache Spark
RUN wget --no-verbose -O apache-spark.tgz "https://archive.apache.org/dist/spark/spark-3.1.2/spark-3.1.2-bin-hadoop3.2.tgz" \
    && mkdir -p /opt/spark \
    && tar -xf apache-spark.tgz -C /opt/spark --strip-components=1 \
    && rm apache-spark.tgz

# Link Spark directory
RUN ln -s /opt/spark-3.1.2-bin-hadoop2.7 /opt/spark
RUN echo 'export SPARK_HOME=/opt/spark' >> ~/.bashrc \
    && echo 'export PATH=$SPARK_HOME/bin:$PATH' >> ~/.bashrc \
    && echo 'export PYSPARK_PYTHON=python3' >> ~/.bashrc

# Create directories
RUN mkdir /code
RUN mkdir /code/data
RUN mkdir /code/data/csv
RUN mkdir /code/data/model
RUN mkdir /code/src
RUN mkdir /code/data/testdata.model/

# Copy application files
COPY src/winequilitytestdataprediction.py /code/src
COPY data/model/testdata.model/ /code/data/model/testdata.model
COPY data/csv/ /code/data/csv

# Configure shell
RUN rm /bin/sh && ln -s /bin/bash /bin/sh

# Source environment variables
RUN /bin/bash -c "source ~/.bashrc"
RUN /bin/sh -c "source ~/.bashrc"

# Set the working directory
WORKDIR /code/

# Set the entry point for the container
ENTRYPOINT ["/opt/spark/bin/spark-submit", "src/winequilitytestdataprediction.py"]