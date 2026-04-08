from dataclasses import dataclass, field
import json
import os


@dataclass
class LogRecord:
    timestamp: str
    bytes_sent: int
    status: str
    remote_addr: str


@dataclass
class IPTrafficSummary:
    ip_address: str
    request_count: int = 0
    pct_requests: float = 0.0
    total_bytes: int = 0
    pct_bytes: float = 0.0


class LogParser:
    """Parses semicolon-separated log files and filters by status."""

    def __init__(self, status_filter: str = "OK") -> None:
        self._status_filter = status_filter

    def parse(self, lines: list[str]) -> list[LogRecord]:
        """Parse log lines, keeping only those matching the status filter."""
        records: list[LogRecord] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            parts = line.split(";")
            if len(parts) != 4:
                continue

            timestamp, bytes_str, status, remote_addr = parts
            if status.strip() != self._status_filter:
                continue

            try:
                bytes_sent = int(bytes_str.strip())
            except ValueError:
                continue

            records.append(LogRecord(
                timestamp=timestamp.strip(),
                bytes_sent=bytes_sent,
                status=status.strip(),
                remote_addr=remote_addr.strip(),
            ))
        return records

    def parse_file(self, file_name: str, input_directory_path: str = 'logfiles') -> list[LogRecord]:
        """Read and parse a log file."""
        
        if not os.path.exists(input_directory_path):
            os.mkdir(input_directory_path)

        file_path = os.path.join(input_directory_path, file_name)
        with open(file_path, "r") as f:
            return self.parse(f.readlines())


class ReportGenerator:
    """Aggregates log records by IP and produces CSV or JSON reports."""
    def __init__(self):
        self.report_formatters = {
            'csv': self.to_csv,
            'json': self.to_json,
        }

    def generate_report(self, log_records: list[LogRecord]) -> list[IPTrafficSummary]:
        """Aggregate log records by IP, compute percentages, sort by request count DESC."""
        ip_traffic_report: dict[str, IPTrafficSummary] = {}
        total_requests = 0
        total_bytes = 0

        for log_record in log_records:
            ip_traffic_report.setdefault(log_record.remote_addr, IPTrafficSummary(ip_address=log_record.remote_addr))
            ip_traffic_report[log_record.remote_addr].request_count += 1
            ip_traffic_report[log_record.remote_addr].total_bytes += log_record.bytes_sent
            total_requests += 1
            total_bytes += log_record.bytes_sent

        for ip_traffic_summary in ip_traffic_report.values():
            ip_traffic_summary.pct_requests = (ip_traffic_summary.request_count / total_requests) if total_requests else 0.0
            ip_traffic_summary.pct_bytes = (ip_traffic_summary.total_bytes / total_bytes) if total_bytes else 0.0

        return sorted(ip_traffic_report.values(), key=lambda r: r.request_count, reverse=True)

    def to_csv(self, rows: list[IPTrafficSummary]) -> str:
        """Format report rows as CSV."""
        header = "IP Address,Number of Requests,Percentage of Total Requests,Total Bytes Sent,Percentage of Total Bytes\n"
        body = ""
        for r in rows:
            body += f"{r.ip_address},{r.request_count},{round(r.pct_requests, 2)},{r.total_bytes},{round(r.pct_bytes, 2)}\n"
        return header + body

    def to_json(self, rows: list[IPTrafficSummary]) -> str:
        """Format report rows as JSON."""
        return json.dumps(
            [
                {
                    "ip_address": r.ip_address,
                    "number_of_requests": r.request_count,
                    "percentage_of_total_requests": round(r.pct_requests, 2),
                    "total_bytes_sent": r.total_bytes,
                    "percentage_of_total_bytes": round(r.pct_bytes, 2),
                }
                for r in rows
            ],
            indent=2,
        )

    def get_report_formatter(self, fmt: str = "csv"):
        try:
            return self.report_formatters[fmt]
        except IndexError:
            raise NotImplemented

    def write_report(self, report: list[IPTrafficSummary], output_file_name: str, output_directory_path: str = 'reports') -> None:
        """Write report to file in the specified format."""
        if not os.path.exists(output_directory_path):
            os.mkdir(output_directory_path)

        output_file_path = os.path.join(output_directory_path, output_file_name)
        export_format = output_file_name.split('.')[-1]
        format_report = self.get_report_formatter(export_format)
        formatted_report = format_report(report)
        with open(output_file_path, "w") as f:
            f.write(formatted_report)


if __name__ == '__main__':
    log_parser = LogParser()
    parsed_ip_records = log_parser.parse_file('requests.log')
    
    report_generator = ReportGenerator()
    report = report_generator.generate_report(parsed_ip_records)
    report_generator.write_report(report, 'ipaddress.csv')

