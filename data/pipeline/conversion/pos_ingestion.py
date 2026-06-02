"""
POS Transaction Ingestion

Reads POS transaction logs and structures them for visitor conversion correlation.
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class POSTransaction:
    """Represents a single POS transaction."""

    def __init__(
        self,
        transaction_id: str,
        timestamp: datetime,
        amount: float,
        payment_method: str = "unknown"
    ):
        self.transaction_id = transaction_id
        self.timestamp = timestamp
        self.amount = amount
        self.payment_method = payment_method

    def to_dict(self) -> Dict:
        return {
            "transaction_id": self.transaction_id,
            "timestamp": self.timestamp.isoformat(),
            "amount": self.amount,
            "payment_method": self.payment_method
        }


class POSIngestionLayer:
    """
    Ingests POS transaction data from various sources.
    
    Supports:
    - JSON format: list of dicts with transaction_id, timestamp, amount
    - CSV format: columns (transaction_id, timestamp, amount)
    """

    def __init__(self, source_path: Optional[str] = None):
        """
        Initialize POS ingestion layer.
        
        Args:
            source_path: Path to POS data file (JSON or CSV)
        """
        self.source_path = source_path
        self.transactions: List[POSTransaction] = []

    def ingest_json(self, file_path: str) -> List[POSTransaction]:
        """
        Ingest POS transactions from JSON file.
        
        Expected format:
        [
            {
                "transaction_id": "TXN_001",
                "timestamp": "2026-05-30T10:05:30Z",
                "amount": 150.00
            },
            ...
        ]
        """
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: POS file not found: {file_path}")
            return []

        try:
            with open(path, "r") as f:
                data = json.load(f)

            if not isinstance(data, list):
                raise ValueError("POS JSON must be a list of transactions")

            transactions = []
            for record in data:
                txn = POSTransaction(
                    transaction_id=record["transaction_id"],
                    timestamp=datetime.fromisoformat(
                        record["timestamp"].replace("Z", "+00:00")
                    ),
                    amount=float(record.get("amount", 0)),
                    payment_method=record.get("payment_method", "unknown")
                )
                transactions.append(txn)

            self.transactions = transactions
            print(f"Ingested {len(transactions)} POS transactions from {file_path}")
            return transactions

        except Exception as e:
            print(f"Error ingesting POS JSON: {e}")
            return []

    def ingest_csv(self, file_path: str) -> List[POSTransaction]:
        """
        Ingest POS transactions from CSV file.
        
        Expected columns: transaction_id, timestamp, amount, payment_method (optional)
        """
        path = Path(file_path)
        if not path.exists():
            print(f"Warning: POS file not found: {file_path}")
            return []

        try:
            transactions = []
            with open(path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    txn = POSTransaction(
                        transaction_id=row["transaction_id"],
                        timestamp=datetime.fromisoformat(
                            row["timestamp"].replace("Z", "+00:00")
                        ),
                        amount=float(row.get("amount", 0)),
                        payment_method=row.get("payment_method", "unknown")
                    )
                    transactions.append(txn)

            self.transactions = transactions
            print(f"Ingested {len(transactions)} POS transactions from {file_path}")
            return transactions

        except Exception as e:
            print(f"Error ingesting POS CSV: {e}")
            return []

    def ingest(self, file_path: str) -> List[POSTransaction]:
        """
        Auto-detect format and ingest POS transactions.
        """
        if file_path.endswith(".json"):
            return self.ingest_json(file_path)
        elif file_path.endswith(".csv"):
            return self.ingest_csv(file_path)
        else:
            raise ValueError(
                f"Unsupported file format: {file_path}. "
                "Must be .json or .csv"
            )

    def get_transactions(self) -> List[POSTransaction]:
        """Return ingested transactions."""
        return self.transactions

    def get_transactions_in_timerange(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[POSTransaction]:
        """Get transactions occurring between start and end times."""
        return [
            txn for txn in self.transactions
            if start_time <= txn.timestamp <= end_time
        ]


def create_sample_pos_file(output_path: str = "data/raw/sample_transactions.json"):
    """Create a sample POS transaction file for testing."""
    sample_data = [
        {
            "transaction_id": "TXN_001",
            "timestamp": "2026-05-30T10:05:00Z",
            "amount": 150.50,
            "payment_method": "credit_card"
        },
        {
            "transaction_id": "TXN_002",
            "timestamp": "2026-05-30T10:10:30Z",
            "amount": 75.25,
            "payment_method": "cash"
        },
        {
            "transaction_id": "TXN_003",
            "timestamp": "2026-05-30T10:15:00Z",
            "amount": 200.00,
            "payment_method": "credit_card"
        },
        {
            "transaction_id": "TXN_004",
            "timestamp": "2026-05-30T10:20:45Z",
            "amount": 99.99,
            "payment_method": "digital_wallet"
        }
    ]
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(sample_data, f, indent=4)
    
    print(f"Created sample POS file: {output_path}")
    return output_path
