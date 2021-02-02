import os
import apache_beam as beam
import argparse
import logging
import sys
import csv
import psycopg2
import io
import numpy as np
import pandas as pd
from datetime import datetime

from apache_beam.io import ReadFromText, WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

from src.utils.database import Database

from src.classes.etl_winery_list import WineryListEtl
from src.classes.etl_sales_weekly import SalesWeeklyEtl

def run(argv=None):
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)


    p = beam.Pipeline(options=PipelineOptions(pipeline_args))

    db = Database(
        host='ec2-34-235-62-201.compute-1.amazonaws.com',
        dbname='d8hsl7f3pqpmpt',
        user='wocmkztqpfdrzf',
        password='352719f3bd91b730f54fa37ec7c7ae3e6f54c5c6d9292b38d51991a7ba965cc5')

    gs_path = 'gs://alo_dataflow_test'
    time_string = datetime.now().strftime("%Y%m%d_%H%M")

    (
        p
        | 'Winery list ETL' >> WineryListEtl(db, gs_path,time_string)
        | 'Weekly sales ETL' >> SalesWeeklyEtl(db, gs_path,time_string)
    )


    p.run().wait_until_finish()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()