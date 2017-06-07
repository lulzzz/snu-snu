# snu-snu
A tool for 'training' the recommendation system used by an online retail giant.
##### The tool is currently under development. It should encompass the following functionality when complete:
1. Automate the process of searching and viewing products, and adding them to lists.
    1. Through interactive command line interface.
    1. Through JSON list of ProductCommand objects.
    1. When installed as a module, through function calls in other scripts.
1. Generate JSON lists of ProductCommand objects based on NLP of arbitrary texts.
1. Serialise recommended products from all sources for later analysis.

##### Dependancies:
- NLTK
- Selenium and ChromeDriver
- Requests
- Pillow
