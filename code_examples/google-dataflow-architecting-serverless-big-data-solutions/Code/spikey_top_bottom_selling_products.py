from __future__ import absolute_import

import argparse
import logging
import re

import apache_beam as beam
from apache_beam import pvalue
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


class SplitItemsBasedOnSalesFn(beam.DoFn):
    
    OUTPUT_TAG_TOP_SELLERS = 'tag_top_sellers'
    OUTPUT_TAG_POOR_SELLERS = 'tag_poor_sellers'
            
    def process(self, element):

        tokens = element.split('\t')
        
        product = tokens[2]
        quantity = int(tokens[len(tokens) - 1])
    
        if quantity >= 90:
            yield pvalue.TaggedOutput(self.OUTPUT_TAG_TOP_SELLERS, product)
    
        elif quantity < 5:
            yield pvalue.TaggedOutput(self.OUTPUT_TAG_POOR_SELLERS, product)


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        required=True,
                        help='Input file to process.')
            
    parser.add_argument('--output',
                        required=True,
                        help='Output prefix for files to write results to.')
                
    known_args, pipeline_args = parser.parse_known_args(argv)
                    
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
                            
    with beam.Pipeline(options=pipeline_options) as p:
                                
        items = p | ReadFromText(known_args.input)
                                    
        split_items_result = (items
                               | beam.ParDo(SplitItemsBasedOnSalesFn()).
                                    with_outputs(SplitItemsBasedOnSalesFn.OUTPUT_TAG_TOP_SELLERS, 
                                                 SplitItemsBasedOnSalesFn.OUTPUT_TAG_POOR_SELLERS))
                                                                                                           
        top_sellers = split_items_result[SplitItemsBasedOnSalesFn.OUTPUT_TAG_TOP_SELLERS]
        poor_sellers = split_items_result[SplitItemsBasedOnSalesFn.OUTPUT_TAG_POOR_SELLERS]
                                                                      
        (top_sellers | 'Write top sellers' >> WriteToText(known_args.output + 'top-sellers'))
        (poor_sellers | 'Write poor_sellers' >> WriteToText(known_args.output + 'poor-sellers'))


if __name__ == '__main__':
    run()
