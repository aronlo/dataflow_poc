
import apache_beam as beam
import argparse

def find_wineries(line, term):
   if term in line:
      yield line

PROJECT='spikey-dtflw'
BUCKET='spikey-df-store'

def run():

   argv = [
      '--project={0}'.format(PROJECT),
      '--job_name=spikey-wineries-job',
      '--save_main_session',
      '--staging_location=gs://{0}/staging/'.format(BUCKET),
      '--temp_location=gs://{0}/staging/'.format(BUCKET),
      '--runner=DataflowRunner'
   ]

   p = beam.Pipeline(argv=argv)

   input_bucket = 'gs://{0}/data/spikey_winery_list.csv'.format(BUCKET)
   output_prefix = 'gs://{0}/output/wineries/california'.format(BUCKET)
   
   search_term = 'California'


   (p
      | 'GetWineries' >> beam.io.ReadFromText(input_bucket)
      | 'GrepWineriesInCalifornia' >> beam.FlatMap(lambda line: find_wineries(line, search_term) )
      | 'WriteToFile' >> beam.io.WriteToText(output_prefix)
   )

   p.run()

if __name__ == '__main__':
   run()
