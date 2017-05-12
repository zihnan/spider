# Spider
Grabing some information of http website about dns information, HTTP HEADER, HTTP CONTENT,and WHOIS recordss, then saving a file which named the file name in the url.

## spider.py
Grab the information from the \<URL\> of website.<br/>

    python spider.py -u <URL>

Grab the information from the \<URL\> and save into a fold which named \<FOLD\>. <br/>

    python spider.py ( -u <URL> | -i <URL_LIST_FILE> ) [--startwith=<OUTPUT_OFFSET>] [-d <FOLD>]

## Feature Extractor
### feature_extractor.py
Extract features vector from sample file which downloaded by spyder.py.

        usage: kkk.py [-h] [-v] [-n] [--startwith STARTWITH] [--quiet] [--debug] [--select EXTRACTORS_DIRECTORY] sample_file [sample_file ...]

        positional arguments:
          sample_file           sample file formated by spyder.py
        
        optional arguments:
          -h, --help            show this help message and exit
          -v, --verbose         display process detail
          -n, --numeric         numeric feature
          --startwith STARTWITH
                                ouput file name offset
          --quiet               display information
          --debug               display debug information
          --select EXTRACTORS_DIRECTORY
                                select extractors directory

                            
### import feature_extractor
In the directory which contain feature_extracor.py and extracotrs directories, you can use `import feature_extractor` to get features extractor.

    import feature_extractor
    with open('sample-file', 'r') as f:
        extractor = feature_extractor.FeatureExtractor(f.readlines())
    print extractor.run()  # return features vector
    
### extractors directory
You can write down different extractors set, and change extractors set by `feature_extractor.set_extractors_path(extractor_directory)`(this function with some problem, but `python feature_extractor.py --select EXTRACTORS_DIRECTORY SAMPLE_FILE` still work fine).
Every extracotr should inherit `extractor.Extractor`, and interface of \_\_init\_\_ method should be with two parameter(one is the major data which this extractor will be extracted features, another is keyword arguments).

    class HttpExtractor(extractor.Extractor):
        def __init__(self, html_str, **kwargs):
            self.feature = [self.method]  # items of this variable will be treated as methods to extract feature while FeatureExtractor.run().
