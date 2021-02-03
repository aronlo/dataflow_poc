import argparse
import unicodedata


import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.transforms import combiners
from time import sleep


PRODUCT_REVENUE_SCHEMA = 'product_name:STRING,product_revenue:FLOAT'

class RevenuePerProduct(beam.DoFn):
    
  def process(self, element):

      time_stamp, product_name, units_sold, retail_price = element.split(",")
      
      revenue = float(units_sold) * float(retail_price)
      product_revenue = (product_name, revenue)

      return [product_revenue]
        

class CalcTotalProductRevenue(beam.DoFn):

  def process(self,product_entry):
      (product, revenue) = product_entry
      
      total_revenue = sum(revenue)
      return [(product,total_revenue)]
     


def format_output_json(element):
    product_name, product_revenue = element

    product_name = unicodedata.normalize('NFKD', product_name).encode('ascii', 'ignore')
    product_revenue = float(product_revenue)

    return [{
        'product_name': product_name,
        'product_revenue': product_revenue,
    }]
  


def run(argv=None):
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--input',
                        dest='input',
                        default='gs://spikey-df-store/data/spikey_sales_weekly.csv',
                        help='Input file to process.')
    parser.add_argument('--output',
                        dest='output',
                        required=True,
                        help='Output file to write results to.')
    
    known_args, pipeline_args = parser.parse_known_args(argv)


    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True

    p = beam.Pipeline(options=pipeline_options) 
    
    (p
    | 'read' >> ReadFromText(known_args.input)  
    | 'Revenue for each product line item' >> (beam.ParDo(RevenuePerProduct())) 
    | 'Group per product' >> (beam.GroupByKey())
    | 'Total revenue per product' >> (beam.ParDo(CalcTotalProductRevenue()))
    | 'Format to json' >> (beam.ParDo(format_output_json))
    | 'Write to BigQuery' >> beam.io.WriteToBigQuery(known_args.output, schema=PRODUCT_REVENUE_SCHEMA)
  )

    result = p.run()
    result.wait_until_finish()


if __name__ == '__main__':
  run()
