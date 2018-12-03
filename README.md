# tokenomics

[![Python](https://img.shields.io/badge/jupiter--notebook-nbviewer-orange.svg)](https://nbviewer.jupyter.org/github/Tingesplatform/tokenomics/blob/master/tokenomics.ipynb)
[![Build Status](https://travis-ci.com/Tingesplatform/tokenomics.svg?branch=master)](https://travis-ci.com/Tingesplatform/tokenomics)
[![Python](https://img.shields.io/badge/python-3.5,%203.6,%203.7-blue.svg)](https://travis-ci.com/Tingesplatform/tokenomics)

## Abstract
Tinges project token economy model in Python. 
The model shows how the received funds power up the Tinges platform development cycles in a controlled and measurable way. 

## Contracts
Invested capital gets locked in a structure of 2 contract types:
* bucket - keeps given amount of funds. If incoming funds overflows the bucket, the next bucket in chain gets filled;
* tap - serves withdrawal requests limiting the amount of money one can reclaim per time interval.

The stack of inter-connected contracts gets configured in line with financial model of the Tinges platform, considering its 
investment and expenditure plans.
The typical structure:

```

 investors
  |  |  |
  V  V  V
  
 \   bkt1  /
  \-------/--+----+overflow
   \     / cap1   |
    \-+-/----+    |
      |           |
     tap1         |
      |           V
                \   bkt2    /
                 \---------/--+-----+overflow
                  \       / cap2    |
                   \-+-+-/----+     |
                     | |            |
               tap2.1| |tap2.2      |
                     | |            V
                                \     bkt3      /
                                 \             /--+-----+overflow
                                  \-----------/ cap3    |
                                   \-+--+--+-/----+     |
                                     |  |  |            |
                                     |  |  |            V
                               tap3.1|  |  |tap3.3   other buckets
                                        |            can be added further
                                        |tap3.3
```

## API
python psewdocode to build the hierarchy looks like:
```
token = ERC20Token()
bkt3 = Bucket(token=token, max_volume=cap3)
bkt2 = Bucket(token=token, max_volume=cap2, overflow_bkt=bkt3)
bkt1 = Bucket(token=token, max_volume=cap1, overflow_bkt=bkt2)
tap1 = Tap(bucket=bkt1, rate=RATE1)
tap2_1 = Tap(bucket=bkt2, rate=RATE2_1)
tap2_2 = Tap(bucket=bkt2, rate=RATE2_2)
tap3_1 = Tap(bucket=bkt3, rate=RATE3_1)
tap3_2 = Tap(bucket=bkt3, rate=RATE3_2)
tap3_3 = Tap(bucket=bkt3, rate=RATE3_3)
```

after the time the person which allowed to use the tap (developer, contractor) 
can reclaim the limited amount of funds from the connected bucket

```
tap3_3.withdraw(N)
```

## Run
To see API in action use tests and/or jupyter notebook

### Test
Install python dependencies and run tests locally
```
pip3 install -r requirements.txt
py.test -v
```

### Online Jupiter NB viewer

The notebook can be opened in online viewer [here](https://nbviewer.jupyter.org/github/Tingesplatform/tokenomics/blob/master/tokenomics.ipynb).

### Offline Jupyter

For better debugging capabilities you can 
[install jupyter notebook](https://jupyter.readthedocs.io/en/latest/install.html) locally and run it in separate console.
Don't forget to satisfy dependencies.
```
pip3 install -r requirements.txt
jupiter notepook
```
it will open local webserver url in browser, then you should open tokenomics.ipynb in it.

## Authors

* [Kirill Varlamov](https://github.com/ongrid), OnGrid Systems ([github](https://github.com/OnGridSystems), [site](https://ongrid.pro))
* [Roman Nesytov](https://github.com/profx5), OnGrid Systems ([github](https://github.com/OnGridSystems), [site](https://ongrid.pro))
