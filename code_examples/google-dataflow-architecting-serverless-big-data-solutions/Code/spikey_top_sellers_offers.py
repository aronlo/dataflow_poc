from __future__ import absolute_import

import argparse
import logging
import re

import apache_beam as beam
from apache_beam import pvalue
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText

from apache_beam.pvalue import AsList
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


class TopSellingProductsFn(beam.DoFn):

    def process(self, element):
    
        tokens = element.split('\t')
        
        product_id = tokens[0]
        product_name = tokens[2]
        quantity = int(tokens[len(tokens) - 1])
    
        if quantity >= 90:
            yield (product_id, product_name)

class GetItemsOnOfferFn(beam.DoFn):
    
    def process(self, element):

        tokens = element.split('\t')
        product_id = tokens[0]

        yield product_id

def match_ids_fn(top_seller, discounted_items):

   if top_seller[0] in discounted_items:
        yield top_seller[1]

def run(argv=None):
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--input1',
                        required=True,
                        help='Input file to process.')
            
    parser.add_argument('--input2',
                        required=True,
                        help='Input file to process.')
                
    parser.add_argument('--output',
                        required=True,
                        help='Output prefix for files to write results to.')
                    
    known_args, pipeline_args = parser.parse_known_args(argv)
                        
    pipeline_options = PipelineOptions(pipeline_args)
                            
    pipeline_options.view_as(SetupOptions).save_main_session = True
                                
    with beam.Pipeline(options=pipeline_options) as p:
                                    
        sold_items = p | 'Read items sold - input 1' >> ReadFromText(known_args.input1)
        offer_applied_items = p | 'Read offers - input 2' >> ReadFromText(known_args.input2)
                                                
        top_selling_products = (sold_items | 'Read product IDs and names' >> beam.ParDo(TopSellingProductsFn()))
                                                    
        offer_applied_ids = (offer_applied_items | 'Find Discounted Product IDs' >> beam.ParDo(GetItemsOnOfferFn()))
         
        top_selling_discounted_products = (top_selling_products | 'Find Discounted Top Sellers' >> beam.FlatMap(match_ids_fn, AsList(offer_applied_ids)))
                                                            
        (top_selling_discounted_products  | 'Write Results' >> WriteToText(known_args.output + 'sold-on-discount'))


if __name__ == '__main__':
    run()
