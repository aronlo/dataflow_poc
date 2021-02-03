
import apache_beam as beam
import sys

def find_wineries(line, term):
   if  term in line:
      yield line

if __name__ == '__main__':
   p = beam.Pipeline(argv=sys.argv)

   input_prefix = 'spikey_winery_list.csv'
   output_prefix = 'output/result'
   
   searchTerm = 'California'

   (p
      | 'GetWineries' >> beam.io.ReadFromText(input_prefix)
      | 'GrepWineriesInCalifornia' >> beam.FlatMap(lambda line: find_wineries(line, searchTerm) )
      | 'WriteToFile' >> beam.io.WriteToText(output_prefix)
   )

   p.run().wait_until_finish()
