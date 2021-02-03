
package org.apache.beam.examples;

import java.util.Arrays;
import java.util.List;
import java.lang.Long;
import java.lang.Double;
import java.lang.StringBuffer;

import org.apache.beam.examples.common.ExampleUtils;
import org.apache.beam.sdk.Pipeline;
import org.apache.beam.sdk.io.TextIO;
import org.apache.beam.sdk.transforms.Combine;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;
import org.apache.beam.sdk.options.PipelineOptions;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.options.Validation.Required;
import org.apache.beam.sdk.transforms.DoFn;
import org.apache.beam.sdk.transforms.MapElements;
import org.apache.beam.sdk.transforms.PTransform;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.transforms.SimpleFunction;
import org.apache.beam.sdk.values.KV;
import org.apache.beam.sdk.values.PCollection;
import org.apache.beam.sdk.transforms.Sum;


public class SpikeyProductRevenue {
  
  static class ExtractProductRevenueFn extends DoFn<String, String> {
    @ProcessElement
    public void processElement(@Element String element, OutputReceiver<String> receiver) {
    
      String[] words = element.split(",");
      
      String productEntry = words[1] + "," + 
        Double.toString(Double.parseDouble(words[2]) * Double.parseDouble(words[3]));
      
      
      receiver.output(productEntry);
    }
 }
 
 static class ExtractProductRevenuePairFn extends DoFn<String, KV<String, Double>> {
    @ProcessElement
    public void processElement(@Element String element, OutputReceiver<KV<String, Double>> receiver) {
    
        String[] tokens = element.split(",");
        
        String productName = tokens[0];
        Double revenue = Double.parseDouble(tokens[1]);
        
        KV<String, Double> pair = KV.<String, Double>of(productName, revenue);
             
        receiver.output(pair);
    }
  
 }

 public static class GenerateProductRevenuePairs
      extends PTransform<PCollection<String>, PCollection<KV<String, Double>>> {
    @Override
    public PCollection<KV<String, Double>> expand(PCollection<String> lines) {
        
        PCollection<KV<String, Double>> productRevenuePairs = 
          lines.apply(ParDo.of(new ExtractProductRevenuePairFn()));
        
        return productRevenuePairs;
    }
  }
 
  public static class FormatAsTextFn extends SimpleFunction<KV<String, Double>, String> {
    @Override
    public String apply(KV<String, Double> input) {
        return input.getKey() + "," + input.getValue();
    }
  }


  public interface RevenueCountOptions extends PipelineOptions {

    @Description("Path of the file to read from")
    @Default.String("gs://spikey-df-store/data/spikey_sales_weekly.csv")
    String getInputFile();

    void setInputFile(String value);

    @Description("Path of the file to write to")
    @Default.String("gs://spikey-df-store/output/revenue/product")
    String getOutput();

    void setOutput(String value);
  }
  

  static void runProductRevenue(RevenueCountOptions options) {
    Pipeline p = Pipeline.create(options);
  
    p.apply("ReadLines", TextIO.read().from(options.getInputFile()))
        .apply("ExtractProductRevenue", ParDo.of(new ExtractProductRevenueFn()))
        .apply("GenerateProductRevenuePairs", new GenerateProductRevenuePairs())
        .apply("TotalRevenuePerProduct", Combine.<String, Double, Double>perKey(Sum.ofDoubles()))
        .apply("ConvertToStrings", MapElements.via(new FormatAsTextFn()))
        .apply("WritePeerProductRevenue", TextIO.write().to(options.getOutput()));

    p.run().waitUntilFinish();
  }

  public static void main(String[] args) {
    RevenueCountOptions options =
        PipelineOptionsFactory.fromArgs(args).withValidation().as(RevenueCountOptions.class);
     
    runProductRevenue(options);
  }
}


