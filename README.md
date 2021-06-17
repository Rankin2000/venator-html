# venator-html
## Installation
### Requirements
- [Venator-Swift](https://github.com/richiercyrus/Venator-Swift)
- [Dominate](https://pypi.org/project/dominate/)

## Usage
The tool is simple to use. 
The recommended use is as follows:
1. Set up a virtual machine with analysis tools required and prior to taking a snapshot generate a baseline using the command: `python3 venator-html.py -g`

   *The baseline is optional, but is required for the filter flag (-f).*

2. Run the sample on the VM,
3. The tool can generate a report by using the command: `python3 venator-html.py -f`

   *The optional filter flag attempts to reduce the output of the report by comparing the venator result with the baseline.*
  
The HTML report can be found under "venator.html"

