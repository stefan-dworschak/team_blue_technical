import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from report_generator import LogParser, LogRecord, ReportGenerator, IPTrafficSummary


class TestLogParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = LogParser()

    def test_parse_valid_ok_lines(self) -> None:
        lines = [
            "2024-01-15T10:00:00;1024;OK;192.168.1.1\n",
            "2024-01-15T10:00:01;2048;OK;192.168.1.2\n",
        ]
        records = self.parser.parse(lines)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].remote_addr, "192.168.1.1")
        self.assertEqual(records[0].bytes_sent, 1024)
        self.assertEqual(records[1].remote_addr, "192.168.1.2")

    def test_filters_non_ok_status(self) -> None:
        lines = [
            "2024-01-15T10:00:00;1024;OK;192.168.1.1\n",
            "2024-01-15T10:00:01;4096;ERROR;192.168.1.2\n",
            "2024-01-15T10:00:02;512;NOT_FOUND;192.168.1.3\n",
        ]
        records = self.parser.parse(lines)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].remote_addr, "192.168.1.1")

    def test_skips_malformed_lines(self) -> None:
        lines = [
            "2024-01-15T10:00:00;1024;OK;192.168.1.1\n",
            "this;is;malformed\n",
            "\n",
            "too;many;fields;here;extra\n",
        ]
        records = self.parser.parse(lines)
        self.assertEqual(len(records), 1)

    def test_skips_invalid_bytes(self) -> None:
        lines = ["2024-01-15T10:00:00;notanumber;OK;192.168.1.1\n"]
        records = self.parser.parse(lines)
        self.assertEqual(len(records), 0)

    def test_empty_input(self) -> None:
        records = self.parser.parse([])
        self.assertEqual(len(records), 0)

    def test_parse_file(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".log", delete=False) as f:
            f.write("2024-01-15T10:00:00;1024;OK;10.0.0.1\n")
            f.write("2024-01-15T10:00:01;512;ERROR;10.0.0.2\n")
            path = f.name
        try:
            records = self.parser.parse_file(path)
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0].remote_addr, "10.0.0.1")
        finally:
            os.unlink(path)

    def test_custom_status_filter(self) -> None:
        parser = LogParser(status_filter="ERROR")
        lines = [
            "2024-01-15T10:00:00;1024;OK;192.168.1.1\n",
            "2024-01-15T10:00:01;4096;ERROR;192.168.1.2\n",
        ]
        records = parser.parse(lines)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].remote_addr, "192.168.1.2")


class TestReportGenerator(unittest.TestCase):
    def setUp(self) -> None:
        self.generator = ReportGenerator()
        self.records = [
            LogRecord("2024-01-15T10:00:00", 1024, "OK", "192.168.1.1"),
            LogRecord("2024-01-15T10:00:01", 2048, "OK", "192.168.1.2"),
            LogRecord("2024-01-15T10:00:02", 512, "OK", "192.168.1.1"),
            LogRecord("2024-01-15T10:00:03", 256, "OK", "192.168.1.1"),
            LogRecord("2024-01-15T10:00:04", 1024, "OK", "192.168.1.2"),
        ]

    def test_generate_report_counts(self) -> None:
        report = self.generator.generate_report(self.records)
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0].ip_address, "192.168.1.1")
        self.assertEqual(report[0].request_count, 3)
        self.assertEqual(report[1].ip_address, "192.168.1.2")
        self.assertEqual(report[1].request_count, 2)

    def test_generate_report_bytes(self) -> None:
        report = self.generator.generate_report(self.records)
        self.assertEqual(report[0].total_bytes, 1792)  # 1024 + 512 + 256
        self.assertEqual(report[1].total_bytes, 3072)  # 2048 + 1024

    def test_generate_report_percentages(self) -> None:
        report = self.generator.generate_report(self.records)
        self.assertAlmostEqual(report[0].pct_requests, 0.6)
        self.assertAlmostEqual(report[1].pct_requests, 0.4)
        self.assertAlmostEqual(report[0].pct_bytes, 0.368421053) 
        self.assertAlmostEqual(report[1].pct_bytes, 0.631578947)

    def test_sorted_by_request_count_descending(self) -> None:
        report = self.generator.generate_report(self.records)
        counts = [r.request_count for r in report]
        self.assertEqual(counts, sorted(counts, reverse=True))

    def test_generate_report_empty_records(self) -> None:
        report = self.generator.generate_report([])
        self.assertEqual(len(report), 0)

    def test_to_csv_format(self) -> None:
        report = [
            IPTrafficSummary("10.0.0.1", 3, 0.6, 1500, 0.75),
            IPTrafficSummary("10.0.0.2", 2, 0.4, 500, 0.25),
        ]
        csv_output = self.generator.to_csv(report)
        expected = (
            "IP Address,Number of Requests,Percentage of Total Requests,Total Bytes Sent,Percentage of Total Bytes\n"
            "10.0.0.1,3,0.6,1500,0.75\n"
            "10.0.0.2,2,0.4,500,0.25\n"
        )
        self.assertEqual(csv_output, expected)

    def test_to_json_format(self) -> None:
        report = [
            IPTrafficSummary("10.0.0.1", 3, 0.6, 1500, 0.75),
        ]
        json_output = self.generator.to_json(report)
        self.assertEqual(
            json.loads(json_output),
            [
                {
                    "ip_address": "10.0.0.1",
                    "number_of_requests": 3,
                    "percentage_of_total_requests": 0.6,
                    "total_bytes_sent": 1500,
                    "percentage_of_total_bytes": 0.75,
                },
            ],
        )

    def test_write_report_csv(self) -> None:
        report = [IPTrafficSummary("10.0.0.1", 1, 1.0, 512, 1.0)]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            path = f.name
        try:
            self.generator.write_report(report, path)
            with open(path) as f:
                content = f.read()
            expected = (
                "IP Address,Number of Requests,Percentage of Total Requests,Total Bytes Sent,Percentage of Total Bytes\n"
                "10.0.0.1,1,1.0,512,1.0\n"
            )
            self.assertEqual(content, expected)
        finally:
            os.unlink(path)

    def test_write_report_json(self) -> None:
        report = [IPTrafficSummary("10.0.0.1", 1, 1.0, 512, 1.0)]
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            path = f.name
        try:
            self.generator.write_report(report, path)
            with open(path) as f:
                data = json.load(f)
            self.assertEqual(
                data,
                [
                    {
                        "ip_address": "10.0.0.1",
                        "number_of_requests": 1,
                        "percentage_of_total_requests": 1.0,
                        "total_bytes_sent": 512,
                        "percentage_of_total_bytes": 1.0,
                    },
                ],
            )
        finally:
            os.unlink(path)
