# MyGene.info

## Description
MyGene.info is a web API for accessing gene annotation information (Gene Annotation Query as a Service).  This repo contains the web front-end of MyGene.info.  For more information see this reference:

> Xin J, Mark A, Afrasiabi C, Tsueng G, Juchler M, Gopal N, Stupp GS, Putman TE, Ainscough BJ, Griffith OL, Torkamani A, Whetzel PL, Mungall CJ, Mooney SD, Su AI, Wu C.
> **High-performance web services for querying gene and variant annotation.**
> Genome Biol. 2016 May 6;17(1):91. doi: 10.1186/s13059-016-0953-9.
> https://www.ncbi.nlm.nih.gov/pubmed/27154141

## Setup Mygene.info Web Server Locally ##


#### 1. Prerequisites

    python (>=3.4)
    git 

   In Ubuntu/Debian system, you can install all prerequisites by


    sudo apt-get install python-dev python-setuptools git 



#### 2. Clone this repo:


    git clone https://github.com/biothings/mygene.info.git


#### 3. Setup a Python "virtualenv" (optional, but highly recommended):


    sudo easy_install pip
    sudo pip install virtualenv

    virtualenv ~/opt/devpy


#### 4. Install required python modules:


    pip install -r ./requirements_web.txt


#### 5. Make your own "config.py" file


    cd src
    vim config.py
    
   >from config_web import *  
   >from config_hub import *  
   >&#35; And additional customizations


#### 6. Run your dev server


    python index.py --debug


or

    python index.py --debug --port=9000
