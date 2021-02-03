from __future__ import print_function

import re
import sys
import time
import argparse
import logging

import datetime
from dateutil.parser import parse as parse_datetime

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


def extract_timestamp(record):
    mo = re.search(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6})', record)
    if mo is not None:
        try:
            dt = parse_datetime(mo.group(0), fuzzy=True)
            return int(time.mktime(dt.timetuple()))
        except Exception:
            pass
    
    return int(time.time())


class AddTimestampDoFn(beam.DoFn):

    def process(self, element):
        ts = extract_timestamp(element)

        yield beam.window.TimestampedValue(element, ts)


class PrintWindowFn(beam.DoFn):

    def process(self, element, window=beam.DoFn.WindowParam):
        start_time = datetime.datetime.fromtimestamp(window.start)
        end_time = datetime.datetime.fromtimestamp(window.end)

        print ('[%s, %s) @ %s' % (start_time.isoformat(), end_time.isoformat(), element))

        return (start_time.isoformat() + ' ' + end_time.isoformat(), element)


def run(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        required=True,
                        help='Input file to process.')
        
    parser.add_argument('--output',
                         required=True,
                         help='Output prefix for files to write results to.')
                        
    known_args, pipeline_args = parser.parse_known_args(argv)
                        
    options = PipelineOptions(pipeline_args)
    options.view_as(SetupOptions).save_main_session = True
                        
    with beam.Pipeline(options=options) as p:
        
        lines = p | 'Create' >> ReadFromText(known_args.input)
                                
        windowed_counts = (
                           lines
                           | 'Timestamp' >> beam.ParDo(AddTimestampDoFn())
                           | 'Window' >> beam.WindowInto(beam.window.SlidingWindows(3600, 1800))
                           | 'WindowCount' >> (beam.CombineGlobally(beam.combiners.CountCombineFn()).without_defaults())
                           )
        windowed_counts =  (
                           windowed_counts
                           | 'Format' >> beam.ParDo(PrintWindowFn())
                           | 'WriteToText' >> WriteToText(known_args.output + 'hourly_sales.txt')
                           )


if __name__ == '__main__':
    run()
