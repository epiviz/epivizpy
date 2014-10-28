EpivizPy
=====

The repository contains base code for Python integration with the Epiviz tool. 
It also contains a demo that exemplifies usage and potential extension. 

To run the Demo
-----

(Optional) Open project using Eclipse PyDev

Launch src/main.py

Use the following commands in the command line to see the demo at work:

**To load demo data** (influenza read coverage, from the *influenza-A.sam* file included): 

```
addData
```

This will output something like:

<pre style="overflow-y: scroll; max-height: 200px"><code>
user input: "addData"
    coverage   end seqName  start
0          3     4       1      1
1          4   416       1      4
2          5   450       1    416
3          6   541       1    450
4          5   568       1    541
5          4   715       1    568
6          5   748       1    715
7          5   820       1    748
8          4   934       1    820
9          5   949       1    934
10         6  1063       1    949
11         5  1085       1   1063
12         4  1396       1   1085
13         5  1422       1   1396
14         6  1481       1   1422
15         5  1534       1   1481
16         4  1543       1   1534
17         5  1569       1   1543
18         4  1570       1   1569
19         5  1593       1   1570
20         4  1727       1   1593
21         5  1745       1   1727
22         6  1821       1   1745
23         8  1835       1   1821
24         9  1836       1   1835
25        10  2045       1   1836
26         9  2070       1   2045
27         8  2301       1   2070
28         6  2302       1   2301
29         4  2303       1   2302
30         3  2304       1   2303
31         1  2305       1   2304
32         3     3       3      2
33         4    99       3      3
34         5   357       3     99
35         6   553       3    357
36         5   559       3    553
37         4   578       3    559
38         3   793       3    578
39         4   804       3    793
40         5   817       3    804
41         4   831       3    817
42         3   841       3    831
43         4   923       3    841
44         3  1178       3    923
45         4  1211       3   1178
46         5  1242       3   1211
47         6  1257       3   1242
48         8  1274       3   1257
49         9  1281       3   1274
50        10  1291       3   1281
51         9  1371       3   1291
52         8  1661       3   1371
53         7  1673       3   1661
54         6  1674       3   1673
55         5  1718       3   1674
56         3  1719       3   1718
57         1  1720       3   1719
58         2     2       2      1
59         5     3       2      2
         ...   ...     ...    ...

[217 rows x 4 columns]
</code></pre>
