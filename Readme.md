# Flow Log Analyzer

## Overview
This project processes **AWS VPC Flow Logs** and matches them against a predefined **lookup table** to categorize traffic based on **destination port and protocol**. 

## Features
- Reads AWS VPC Flow Logs from a **text file**.
- Parses a **lookup table** (CSV file) to map **destination port & protocol** combinations to specific tags.
- Uses the **official IANA protocol numbers CSV** to convert **protocol numbers to their names** (e.g., `6` → `tcp`).
- Generates **tag counts** and **port-protocol count statistics**.

## Data Files

### 1. Flow Log File (flowlog.txt)
The Flow log follows AWS VPC Flow Logs format: (https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html)

### 2. Lookup table (lookuptable.csv)
A CSV file mapping **destination ports and protocols** to **tags**

### 3. IANA Protocol Numbers CSV (Downloaded from IANA, protocol-numbers-1.csv)
The csv file is downloaded from https://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml that provide mappings of protocol keyword and protocol number. 

## Usage Instruction
1. Install dependencies
```
pip3 install csv
```

2. Run the flow log analyzer (data.py)
```
python3 data.py
```

3. Examine the output in output.txt
Output.txt follows the format of including
- Tag Counts
- Port/Protocol Combination Counts

4. Run the test in test.py
```
python3 test_parser.py
```

## Repo structure
- analyze.py → Main script that processes the flow log and lookup table.
- flowlog.txt → Sample input AWS flow log file.
- lookup_table.csv → Mapping of destination ports & protocols to tags.
- protocol-numbers.csv → Official IANA protocol mappings (e.g., 6 → tcp).
- README.md → Project documentation.

## Assumptions made in implementation
1. This log analyzer only support version 2 of AWS VPC Flow Log. 

2. The flow log format strictly follows the AWS VPC Flow Log structure, with fields appearing in the documented order. The analyzer will skip malformed log, i.e log with missing fields. 

3. The combination of destination port and protocol not found in the current lookup table is
categorized as untagged. 

4. The flow log may contain empty lines, which are skipped. 

5. The matching of tag is case-insensitive. 

6. The ouput file format is .txt and follows the same structure of the provided example. 