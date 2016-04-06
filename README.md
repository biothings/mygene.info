This project is a web front-end of next generation (v2) of MyGene.info (Gene Annotation Query as a Service)

## Setup mygene.info working folder ##


#### 1. Prerequisites

    python (>=2.7)
    git 

   In Ubuntu/Debian system, you can install all prerequisites by


    sudo apt-get install python-dev python-setuptools git 



#### 2. Clone this repo:


    git clone https://github.com/SuLab/mygene.info.git


#### 3. Setup a Python "virtualenv" (optional, but highly recommended):


    sudo easy_install pip
    sudo pip install virtualenv

    virtualenv ~/opt/devpy


#### 4. Install required python modules:


    pip install -r ./requirements.txt


#### 5. Make your own "config.py" file


    cd src
    cp config.py.exmaple config.py


Make changes if needed.

#### 6. Run your dev server


    cd src
    python index.py --debug


or

    python index.py --debug --port=9000
