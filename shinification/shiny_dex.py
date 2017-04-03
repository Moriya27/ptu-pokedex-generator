import copy
import json
import re
from collections import OrderedDict

with open('ptu_pokedex_1_05_plus.json') as infile:
	dex=json.load(infile, object_pairs_hook=OrderedDict)

with open('hatch_rate.json') as infile:
	hatch=json.load(infile, object_pairs_hook=OrderedDict)

string = r"""%Note: Might need to be processed twice to get the ToC working properly
\documentclass{book}
\usepackage{graphicx}
\usepackage{pdfpages}
\usepackage{hyperref}
\usepackage{fancyhdr}
\usepackage{multicol}
\usepackage[letterpaper, margin=1in]{geometry}

\fancyhf{} % clear all header and footers
\renewcommand{\headrulewidth}{0pt} % remove the header 
\fancyfoot[LE,RO]{\thepage}

\pagestyle{fancy}

\begin{document}
\thispagestyle{fancy}
\pagenumbering{Roman} 
\begin{multicols}{2}
\tableofcontents
\end{multicols}
\clearpage\phantomsection

\pagenumbering{arabic}
"""

i=1
arr = []
for item in dex:
	if dex[item]["Species"] in hatch.keys() and not(dex[item]["Species"] in arr):
		arr.append(dex[item]["Species"])
		string = string + "\n"+r"\phantomsection" + "\n" + r"\addcontentsline{toc}{section}{"+dex[item]["Species"]+"}"
		
	string = string + "\n" + r"\includepdf[pages="+str(i)+r",linktodoc,linktodocfit=/Fit,pagecommand={\thispagestyle{fancy}}]{basic_dex.pdf}"+"\n"+r"\newpage"
	i = i + 1

string = string + "\n" + "\end{document}"

with open('shiny_dex.tex', 'w') as outfile:
	outfile.write(string.encode("utf-8"))

print "Done"

#%\setboolean{@twoside}{false}

#%\includepdf[pages=-, pagecommand={\thispagestyle{fancy}}]{dex.pdf}

