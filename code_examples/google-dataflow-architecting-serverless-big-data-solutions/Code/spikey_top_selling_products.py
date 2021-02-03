
import argparse
import logging

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from apache_beam.transforms import combiners
from time import sleep



class RevenuePerProduct(beam.DoFn):
    
  def process(self, element):
      
      logging.info('**SpikeyLogs**: Extract product revenue')

      time_stamp, product_name, units_sold, retail_price = element.split(",")
      
      revenue = float(units_sold) * float(retail_price)
      product_revenue = (product_name, revenue)

      return [product_revenue]
        

class CalcTotalProductRevenue(beam.DoFn):

  def process(self,product_entry):
      (product, revenue) = product_entry
      
      sleep(1)

      total_revenue = sum(revenue)
      return [(product,total_revenue)]
     

def top_revenue_products(products_sold):
    logging.info("**SpikeyLogs: Calculate the top products.")

    def sort_price(product_entry):
        return product_entry[1]

    products_sold.sort(key=sort_price, reverse=True)
    top_selling_ten_products =  products_sold[0:10]

    return top_selling_ten_products



def format_output(product_list):
    output = ""
  
    for product in product_list:
        product_name, revenue = product
        output += product_name.encode('utf8') + "," + str(revenue)
        output += "\n"

    return output
  


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
    | 'Convert to list' >> combiners.ToList()
    | 'Find top N' >> (beam.Map(top_revenue_products))
    | 'Format to string' >> beam.Map(format_output)
    | 'Write output' >> WriteToText(known_args.output)
  )

    result = p.run()
    result.wait_until_finish()


if __name__ == '__main__':
  run()
