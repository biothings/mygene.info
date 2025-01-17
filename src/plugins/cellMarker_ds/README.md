<!-- PROJECT LOGO -->
<br />
<div align="center">
<h3 align="center">CellMaker_DataParser</h3>

  <p align="center">
    This repo contains code that parses raw CellMarker_Data into a JSON file that Dumper can use in Biothings Studio.
    <br />
    </p>
</div>


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About the dataset</a>
    </li>
    <li>
      <a href="#getting-started">Dataset Features</a>
    </li>
    <li><a href="#usage">Data Processing Workflow</a></li>
    <li><a href="#Export JSON file outline">Export JSON file outline</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About the dataset

<!-- [![Product Name Screen Shot][product-screenshot]](https://example.com) -->

About this dataset:
The dataset can be found [here](http://xteam.xbio.top/CellMarker/download.jsp). These records contain data about molecules expressed on the surface, within, or secreted by cells. These markers are used to identify and classify the types, states, or functions of cells within a population. 

### Dataset Schema
There in total 4 different different Cell_Marker Dataset but all of them have the same attributes.
- **speciesType**: the species from which the data originates
    - there are only two data type, either `Human` or `Mouse`
- **tissueType**: the type of tissues from which data originates
    - in total 181 different kinds of cells
    - a lot of them are undefined
- **UberonOntologyID**: The universal unique identifier of the anatomy structure found in animals 
    - needs to confirm with the team
    - contain missing value and most of them are missing due to undefined tissueType
- **cancerType**: the association of the cell marker with the cancer name
    - if the cell Marker does not represent cancer, then it is named as `Normal`
- **cellName**: the English name of the cell that the marker belongs to
- **CellOntologyID**: The universal unique identifier of the cell that the marker belongs to
    - contain missing value
- **cellMarker**: a marker molecule of the cell
    - in string like list, can be converted to a list
- **geneSymbol**: gene expression of the cell marker
    - in string like list, can be converted to a list
- **geneID**: The universal unique identifier of the gene
    - in string like list, can be converted to a list
    - contain missing value
- **proteinName**: name of the protein
    - in string like list, can be converted to a list
    - contain missing value
- **proteinID**: The universal unique identifier of the protein
    - in string like list, can be converted to a list
- **markerResource**: the type of resource or methodology used to identify the marker
    - there are only four data types, either `Experiment` or `Single-cell sequencing` or `Company` or `Review`
- **PMID**: The PudMed ID for the publication or study where the marker data was reported
    - if the `markerResource` is  value company, the the value here is contains `company`
- **Company**: the company associated with the resources
    - most of them are missing and only exist when the `markerResource` is Company

### Data Set relationships
![Product Name Screen Shot](img/CellMarker_Data_relationships.png)

<!-- Dataset Features -->
## Dataset Features
This section will discuss some of the features of the data set. All of the work can be found in the ([Jupyter Notebook](https://github.com/g7xu/CellMaker_DataParser/blob/main/eda/all_cell_eda.ipynb)) in the EDA folder.

### Missingness of UberonOntologyID
Most of the missing UberonOntologyID is due to "Undefined" tissue-type

### Missingness of CellOntologyID
Most of the missing CellOntologyID is due to "Cancer stem cell" in cellName

### Missingness of geneSymbol and geneID
They either exist or are missing at the same time

### Missingness of proteinName and proteinID
They either exist or are missing at the same time

### list-like str value in columns
In the following columns:
- `geneSymbol`
- `geneID`
- `proteinName`
- `proteinID`

values are stored in list-like strings. Here are Example of strings:
- "A"
- "A, B"
- "A B"
- "A, [A, B], C"
- "A, B, C, D, [E, F], [G, H I]"
- NaN (missing value)
  
We expected the parsing result to be:
- ['A']
- ['A', 'B']
- ['A B']
- ['A', ['A', 'B'], 'C']
- ['A', 'B', 'C', 'D', ['E', 'F'], ['G', 'H I']]
- ['NA']

PS. I convert missing value to ['NA'] is for the purpose of finding mismatch value

### Element mismatch among the list-like str value columns
some of the CellMarker records contain mismatch values in its list-like strs. Mismatch values means in a single record, the number of elements in the columns [`geneSymbol`, `geneID`, `proteinName`, `proteinID`] is not the same. For example, in a single record, if there are 5 elements in the `geneSymbol` and 4 elements in `geneID`, this record will be recognized as a record with mismatch values. So far, we have identified two kinds of mismatch:
1. Additional NA at the end
![Mismatch example #1](img/Mismatch_example1.png)
2. total mismatch
![Mismatch example #2](img/Mismatch_example2.png)
![Mismatch example #3](img/Mismatch_example3.png)

**Such mismatch needed to carefully disucss since the the information in these reocrd might not corresponding to each other at all**. In total there are 28 mismatched records(0.6% of the entire dataset). And of these mismatched records, majority of them come from single-cell sequencing.

![Mismatch pie chart](img/mt_MakerDistribution.png)

#### resolution
The relationship between protein and gene in nature is 1 to N. Therefore, there can never be guarantee that the dataset is 1 to 1 match. Thus, **we will drop column `proteinName` and `proteinID`**

### Missingness of company value
91% of the value in the `company` column is missing, but it is missing by design. There are in total 4 different kinds of values in `markerResource` column which are "Experiment", "Review", "Single-cell sequencing", and "Company". The `company` column is not missing when the value in `markerResource` column is "company" 

<!-- Export JSON file outline -->
## Export JSON file outline
This is the template for the output data field. The structure within the cellMarkers field can follow two different formats, depending on the value of the markerResource attribute:
- When markerResource is “Experiment,” “Single-cell sequencing,” or “Review”: The cellMarkers field includes the attribute PMID.
- When markerResource is “Company”: The cellMarkers field includes the attribute Company.

```python
{
  "_id": geneID,
  "symbol": geneSymbol,
  "geneRelatedCells": {
    "CellOntologyID": CellOntologyID
    "cellName": cellName
    "cellType": cellType
    "cancerType": cancerType，
    "tissueType": tissueType,
    "UberonOntologyID": UberonOntologyID,
    "speciesType": speciesType,
    "markerResource": either "Experiment", "Single-cell sequencing", "Review"
    "PMID": PMID
    },
    {
    "CellOntologyID": CellOntologyID
    "cellName": cellName
    "cellType": cellType
    "cancerType": cancerType，
    "tissueType": tissueType,
    "UberonOntologyID": UberonOntologyID,
    "speciesType": speciesType,
    "markerResource": "Company"
    "Company": Company_Name
    }
  }
}
```
## Example
let's look at an example on how the data is being structured following the template above. The data here is:

| speciesType   | tissueType      | UberonOntologyID   | cancerType   | cellType    | cellName                   |   CellOntologyID | markerResource         |     PMID |   Company | cellMarker                      | geneSymbol   |   geneID |
|:--------------|:----------------|:-------------------|:-------------|:------------|:---------------------------|-----------------:|:-----------------------|---------:|----------:|:--------------------------------|:-------------|---------:|
| Human         | Kidney          | UBERON_0002113     | Normal       | Normal cell | Proximal tubular cell      |              nan | Experiment             |  9263997 |       nan | Intestinal Alkaline Phosphatase | ALPI         |      248 |
| Human         | Small intestine | UBERON_0002108     | Normal       | Normal cell | Enterocyte progenitor cell |              nan | Single-cell sequencing | 29802404 |       nan | ALPI                            | ALPI         |      248 |

The resulting data field should be:
```python
{
    '_id': '248',
    'symbol': 'ALPI',
    'geneRelatedCells': [
        {
            'cellName': 'Proximal tubular cell',
            'cellType': 'Normal cell',
            'cancerType': 'Normal',
            'tissueType': 'Kidney',
            'UberonOntologyID': 'UBERON_0002113',
            'speciesType': 'Human',
            'markerResource': 'Experiment',
            'PMID': '9263997'
        },
        {
            'cellName': 'Enterocyte progenitor cell',
            'cellType': 'Normal cell',
            'cancerType': 'Normal',
            'tissueType': 'Small intestine',
            'UberonOntologyID': 'UBERON_0002108',
            'speciesType': 'Human',
            'markerResource': 'Single-cell sequencing',
            'PMID': '29802404'
        },
    ]
}
```
Notice, we are using the first template since the markerResource is either Experiment or Single-cell sequencing.

<!-- Data Processing Workflow -->
## Data Processing Workflow

- concatenating **all_cell_markers** dataframe and **all_singleCell_markers** dataframe
- drop `proteinName` and `proteinID` columns
- remove all rows with missing "geneID"
- replacing all the "undefined" in `tissueType` column with NaN value
- converting all the listLikeStrings into the list for column [cellMarker, geneSymbol, geneID] 

- sometimes, there are duplicate rows within the dataset


<!-- CONTACT -->
## Contact

Guoxuan Xu - [@github_profile](https://github.com/g7xu) - g7xu@ucsd.edu


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* Apperciate Dr. Chunlei Wu and Jason Lin for the help!
