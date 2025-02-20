import csv

DST_PORT_COLUMN_INDEX = 6
PROTOCOL_COLUMN_INDEX = 7
LOG_LINE_LENGTH = 14

LOOKUP_TABLE_COLUMNS = ["dstport", "protocol", "tag"]
PROTOCOL_COLUMNS = ["decimal", "keyword"]

PROTOCOL_FILE = 'protocol-numbers-1.csv'
FLOWLOG_FILE = 'flowlog.txt'
LOOKUP_TABLE_FILE = 'lookuptable.csv'

# build a dictionary that map each protocol number to a protocol name
def build_protocol_dict(protocol_file):
    protocol_dict = {}
    with open(protocol_file, 'r') as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        for row in reader:
            protocol_dict[row[PROTOCOL_COLUMNS[0]]] = row[PROTOCOL_COLUMNS[1]].lower()
    return protocol_dict

# read the flow log line by line
# and return a list that include eeach line as a list
def read_log(flowlog):
    flowlog_list = []
    with open(flowlog, 'r') as file:
        for line in file:
            line_list = line.strip().split()
            if line_list: #skip empty lines
                flowlog_list.append(line_list)
    # print(flowlog_list)
    return flowlog_list

# read the lookup table line by line
# return a dictionary that map each port/protocol combination to a tag
def read_table(lookuptable):
    lookup_table = {}
    with open(lookuptable, 'r') as file:
        reader = csv.DictReader(file)
        reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
        for row in reader:
            dstport = row[LOOKUP_TABLE_COLUMNS[0]]
            protocol = row[LOOKUP_TABLE_COLUMNS[1]].lower() 
            tag = row[LOOKUP_TABLE_COLUMNS[2]]

            lookup_table[(dstport, protocol)] = tag
    return lookup_table

# Count matches for each line in the flow log against the lookup file
# return a dictionary that map each tag to a count
# and a dictionary that map each port/protocol combination to a count
def tag_match_count(flowlog_list, lookup_table, protocol_dict):
    tag_count = {}
    port_protocol_count = {}

    for flowlog in flowlog_list:
        if len(flowlog) < LOG_LINE_LENGTH:
            continue # Skip lines with malformed data

        dstport = flowlog[DST_PORT_COLUMN_INDEX]
        protocol_num = flowlog[PROTOCOL_COLUMN_INDEX]
        protocol = protocol_dict[protocol_num]

        if (dstport, protocol) in lookup_table:
            tag = lookup_table[(dstport, protocol)]
            tag_count[tag] = tag_count.get(tag, 0) + 1
        else:
            tag_count['Untagged'] = tag_count.get('Untagged', 0) + 1
        port_protocol_count[(dstport, protocol)] = port_protocol_count.get((dstport, protocol), 0) + 1

    return tag_count, port_protocol_count


if __name__ == "__main__":
    # Read the flow log and the lookup table file
    # transform to list and dictionary
    protocol_dict = build_protocol_dict(PROTOCOL_FILE)
    flowlog_list = read_log(FLOWLOG_FILE)
    lookup_table = read_table(LOOKUP_TABLE_FILE)

    # output file that contains Count of matches for each tag and 
    # Count of matches for each port/protocol combination 
    output_file = open('output.txt', 'w')
    tag_count = {}
    port_protocol_count = {}

    tag_count, port_protocol_count = tag_match_count(flowlog_list, lookup_table, protocol_dict)
    
    # Write the count statistics to the output file
    with open('output.txt', 'w') as output_file:
        output_file.write("Tag Counts:\n")
        output_file.write("Tag,Count\n")
        for tag, count in tag_count.items():
            output_file.write(f"{tag}: {count}\n")

        output_file.write("\nPort/Protocol Combination Counts:\n")
        output_file.write("Port,Protocol,Count\n")
        for (dstport, protocol), count in port_protocol_count.items():
            output_file.write(f"{dstport},{protocol},{count}\n")
