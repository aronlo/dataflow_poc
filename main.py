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

from apache_beam.io import ReadFromText, WriteToText
from apache_beam.options.pipeline_options import PipelineOptions

from utils.database import Database
from schema.wine import WineSchema

from sqlalchemy import create_engine

from apache_beam.dataframe.convert import to_dataframe
from apache_beam.dataframe.convert import to_pcollection
from beam_nuggets.io import relational_db


def insertDataframe(df):

    towrite = io.BytesIO()
    tmp_df = "./tmp/tmp_dataframe.csv"

    df.to_csv(tmp_df, index_label='id', header=True, index= False, sep =',')

    f = open(tmp_df, 'r')

    db = Database(
        host='ec2-34-235-62-201.compute-1.amazonaws.com',
        dbname='d8hsl7f3pqpmpt',
        user='wocmkztqpfdrzf',
        password='352719f3bd91b730f54fa37ec7c7ae3e6f54c5c6d9292b38d51991a7ba965cc5')

    conn = db.get_conn()
    
    cur = conn.cursor()

    try:
        cur.execute('DROP TABLE IF EXISTS wines;')
        cur.execute('CREATE TABLE wines (id serial PRIMARY KEY, winery varchar, variety varchar, province varchar, country varchar, points integer, price decimal);')

        sql = f'''
        COPY wines
        FROM stdin
        WITH (
          FORMAT 'csv',
          FREEZE 'false',
          DELIMITER ',',
          NULL '',
          HEADER 'true',
          QUOTE '"',
          ESCAPE '\\',
          ENCODING 'utf-8'
        )
        '''
        cur.copy_expert(
        sql=sql,
        file=f)
        conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        #os.remove(tmp_df)
        print("Error: %s" % error)
        conn.rollback()
        cur.close()
        return 1
    print("copy_from_file() done")
    cur.close()
    f.close()
    #os.remove(tmp_df)
    
class FormatElementToObjectDoFn(beam.DoFn):
    def process(self, element):
        el = csv.reader([element], delimiter=',',  quotechar='"')
        el = [ '{}'.format(x) for x in list(csv.reader([element], delimiter=',', quotechar='"'))[0] ]
        try:
            yield {
                'id': int(el[0]),
                'winery': el[1],
                'variety': el[2],
                'province': el[3],
                'country': el[4],
                'points': int(el[5]),
                'price': float(el[6]) if el[6] != '' else 0
            }
        except Exception as e:
            yield beam.pvalue.TaggedOutput('error', element)
            logging.error(f'Error parsing: {e} -> {el} ')

class FormatElementToStringDoFn(beam.DoFn):
    def process(self, element):
        text = f"{element['id']},{element['winery']},{element['variety']},{element['province']},{element['country']},{element['points']},{element['price']}"
        yield text

def run(argv=None):
    parser = argparse.ArgumentParser()
    known_args, pipeline_args = parser.parse_known_args(argv)

    input_files = './datasets/spikey_winery_list/split_*.csv'
    output_raw = './output/raw'
    output_error = './output/error'

    p = beam.Pipeline(options=PipelineOptions(pipeline_args))

    data = (p
        | 'Read csv' >> ReadFromText(input_files, skip_header_lines=True)
        | 'Transform string line to an object' >> beam.ParDo(FormatElementToObjectDoFn()).with_outputs('error', main='formated_pcoll')
    )

    error  = data['error']
    (error 
        | 'Write lines with errors in a file' >>  WriteToText(output_error, file_name_suffix='.txt')
    )

    formated_pcoll = data['formated_pcoll']
    (formated_pcoll 
        | 'Formart to string' >> beam.ParDo(FormatElementToStringDoFn())
        | 'Write data' >>  WriteToText(output_raw, file_name_suffix='.csv', header='id,winery,variety,province,country,points,price')
    )

    (formated_pcoll
        | beam.combiners.ToList()
        | beam.Map(lambda element_list: pd.DataFrame(element_list))
        | beam.Map(lambda df: insertDataframe(df))
    )


    p.run().wait_until_finish()

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.ERROR)
    run()