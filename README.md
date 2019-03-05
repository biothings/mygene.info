Web front-end of next generation (v2) MyGene.info (Gene Annotation Query as a Service)

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
   >#additional customizations


#### 6. Run your dev server


    python index.py --debug


or

    python index.py --debug --port=9000
