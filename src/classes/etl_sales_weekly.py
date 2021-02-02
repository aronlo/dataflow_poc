import os
import apache_beam as beam
import logging
import csv
import psycopg2
import pandas as pd

from apache_beam.io import ReadFromText, WriteToText

from src.utils.database import Database

from datetime import datetime

class FormatElementToObjectDoFn(beam.DoFn):
    def process(self, element):
        el = [ '{}'.format(x) for x in list(csv.reader([element], delimiter=',', quotechar='"'))[0] ]
        try:
            yield {
                'time_stamp': datetime.strptime(el[0], '%Y-%m-%d %H:%M:%S.%f'),
                'product_name': el[1],
                'units_sold': int(el[2]),
                'retail_price': float(el[3])
            }
        except Exception as e:
            yield beam.pvalue.TaggedOutput('error', element)
            #logging.error(f'Error parsing: {e} -> {el}')
            logging.error('Error parsing: {error} -> {element}'.format(error=e, element= element))


class FormatElementToStringDoFn(beam.DoFn):
    def process(self, element):
        text = "{0},{1},{2},{3}".format(element['time_stamp'],
                                          element['product_name'],
                                          element['units_sold'],
                                          element['retail_price'])
        #text = f"{element['time_stamp']},{element['product_name']},{element['units_sold']},{element['retail_price']}"
        yield text

class InsertDB(beam.DoFn):
  def __init__(self, db):
    self._db = db

  def setup(self):
    self._conn = self._db.get_conn()
    self._cur = self._conn.cursor()

  def process(self, df):
    tmp_df = "./tmp/sales_weekly_dataframe.csv"
    df.to_csv(tmp_df, header=True, index= False, sep =',')
    f = open(tmp_df, 'r')
    try:
        self._cur.execute('DROP TABLE IF EXISTS sales_weekly;')
        self._cur.execute('CREATE TABLE sales_weekly (time_stamp date, product_name varchar, units_sold integer, retail_price decimal);')

        sql = "COPY winery_list FROM stdin WITH (FORMAT 'csv', FREEZE 'false', DELIMITER ',', NULL '', HEADER 'true', QUOTE '\"', ESCAPE '\\', ENCODING 'utf-8')"
        self._cur.copy_expert(
        sql=sql,
        file=f)
        self._conn.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logging.error("Error: %s" % error)
        self._conn.rollback()

    f.close()
    os.remove(tmp_df)
    yield df

  def teardown(self):
    self._cur.close()
    self._conn.close()


class SalesWeeklyEtl(beam.PTransform):

  def __init__(self, db, gs_path, time_string):
    self.db = db
    self.input_files = '{0}/datasets/spikey_sales_weekly/split_*.csv'.format(gs_path)
    self.output_raw = '{0}/output/{1}/raw_sales'.format(gs_path, time_string)
    self.output_error = '{0}/output/{1}/error_sales'.format(gs_path, time_string)

  def expand(self, pcoll):

    data = (
      pcoll
      | 'Read winery list csv' >> ReadFromText(self.input_files, skip_header_lines=True)
      | 'Transform string line to an object' >> beam.ParDo(FormatElementToObjectDoFn()).with_outputs('error', main='formated_pcoll')
    )

    # Data OK
    formated_pcoll = data['formated_pcoll']

    (
      formated_pcoll 
      | 'Format to string' >> beam.ParDo(FormatElementToStringDoFn())
      | 'Write winery data to csv' >>  WriteToText(self.output_raw, file_name_suffix='.csv', header='time_stamp,product_name,units_sold,retail_price')
    )

    # Creamos un dataframe a partir del PCollection
    (formated_pcoll
        | beam.combiners.ToList()
        | beam.Map(lambda element_list: pd.DataFrame(element_list))
        | beam.ParDo(InsertDB(self.db))
    )

    # Data con error
    error  = data['error']
    (
      error 
      | 'Write lines with errors in a file' >>  WriteToText(self.output_error, file_name_suffix='.txt')
    )

    return pcoll