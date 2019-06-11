We ran the onr integrated tool chain on 18 projects. This is recorded
in "results_18_projects". However, we found that 6 of these projects
were not being processed correctly by the JInliner tool. We stripped
this for "results_12_projects". We found a further 5 projects had
failing test cases. These are stripped in "results_7_projects".

Each directory contains "all.csv" which displays the data in full and
"*.dat" files which break down the percentage reduction distributions
for each of the configurations.
