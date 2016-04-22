# pb138-address-visualisation

Goal of this project is to create a tool that lets you analyze, process and visualize statistical information from country addresses (ex. street with longest name, most common street name, etc).
This is a school project.
Mainly works with Czech address registry (RUIAN "Výměnný formát"), but it should be extensible enough to use any input (if you write your own parser) or generate any output (if you create your own generator).

## Modules
- Parser
- Visualisers
- Generator

### Parser
- written in Python
- input: one XML file containing address information
- output: XML database in specified directory
- with custom parser input can be basically anything

### Visualisers
- lots of smaller modules
- can be written in any programming language (we mainly use Python through)
- input: database folder (with known structure)
- output: single XML file containing drawing information (what to draw on map, ex. point on coordinates x, y)
- example visualiser: longest street in region - walks through all regions and finds longest street in each of them

### Generator
- written in Python
- input: folder with XML files containing drawing information
- output: single HTML file with drawing information in JSON and JavaScript code to draw on map
- with custom generators output can be changed to basically anything
