## snusnu
A tool for 'training' the recommendation system used by the online retail giant Amazon. This package is not also partly useable via the web application http://rars.online.

#### Basic use

install the package

    pip install git+https://github.com/simoncrowe/snusnu.git
Run your python interpreter. i.e.

    python3
Use the basic terminal interface

    from snusnu import terminal

##### The tool is currently under development. It now emcompasses all of the following functionality although the implementation may not be perfect:
1. Automate the process of searching and viewing products, and adding them to lists.
    1. Through interactive command line interface.
    1. Through JSON list of ProductCommand objects.
    1. When installed as a package, through function calls in other scripts.
1. Generate JSON lists of ProductCommand objects based on NLP of arbitrary texts. **Note:** the NLP part of this functionality has been moved to https://github.com/nlp-frequency-analysis-snusnu
1. Serialise recommended products as JSON and present them as HTML for later analysis.

#### Dependancies:
- Selenium and ChromeDriver
- Requests
- Pillow
