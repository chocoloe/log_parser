import unittest
import tempfile
import os
from parser import build_protocol_dict, read_log, read_table, tag_match_count

class TestDataParsing(unittest.TestCase):
    def setUp(self):
        # Create a temporary protocol file with sample data
        self.protocol_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.protocol_file.write("decimal,keyword\n6,tcp\n17,udp\n1,icmp\n")
        self.protocol_file.seek(0)
        self.protocol_file.close()

        # Create a temporary flow log file with one sample record.
        # Flow log fields: index 6 = dstport, index 7 = protocol number.
        # Sample line:
        # 2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
        self.flowlog_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.flowlog_file.write(
            "2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK\n"
        )
        self.flowlog_file.seek(0)
        self.flowlog_file.close()

        # Create a temporary lookup table file with sample mapping.
        # Mapping the combination of dstport "49153" and protocol "tcp" to "example_tag".
        self.lookup_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.lookup_file.write("dstport,protocol,tag\n49153,tcp,example_tag\n")
        self.lookup_file.seek(0)
        self.lookup_file.close()

    def tearDown(self):
        os.remove(self.protocol_file.name)
        os.remove(self.flowlog_file.name)
        os.remove(self.lookup_file.name)

    def test_build_protocol_dict(self):
        protocol_dict = build_protocol_dict(self.protocol_file.name)
        self.assertEqual(protocol_dict.get("6"), "tcp")
        self.assertEqual(protocol_dict.get("17"), "udp")
        self.assertEqual(protocol_dict.get("1"), "icmp")

    def test_read_log(self):
        flowlog_list = read_log(self.flowlog_file.name)
        # Ensure one record is parsed and verify the dstport and protocol number positions.
        self.assertEqual(len(flowlog_list), 1)
        self.assertEqual(flowlog_list[0][6], "49153")  # dstport at index 6
        self.assertEqual(flowlog_list[0][7], "6")       # protocol number at index 7

    def test_read_table(self):
        lookup_table = read_table(self.lookup_file.name)
        # Verify that the key (dstport, protocol) is in the lookup table
        self.assertIn(("49153", "tcp"), lookup_table)
        self.assertEqual(lookup_table.get(("49153", "tcp")), "example_tag")

    def test_tag_match_count(self):
        protocol_dict = build_protocol_dict(self.protocol_file.name)
        flowlog_list = read_log(self.flowlog_file.name)
        lookup_table = read_table(self.lookup_file.name)
        tag_count, port_protocol_count = tag_match_count(flowlog_list, lookup_table, protocol_dict)
        
        # Check that the flow log record maps correctly to the lookup tag.
        self.assertEqual(tag_count.get("example_tag", 0), 1)
        
        # Verify that there are no untagged entries in this simple test.
        self.assertEqual(tag_count.get("Untagged", 0), 0)
        
        # Check that the port/protocol count was recorded correctly.
        self.assertIn(("49153", "tcp"), port_protocol_count)
        self.assertEqual(port_protocol_count.get(("49153", "tcp")), 1)

if __name__ == "__main__":
    unittest.main()
