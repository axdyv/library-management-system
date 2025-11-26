#!/usr/bin/env python3
"""
load_data.py

Loads normalized CSV files from Milestone 1 into a MySQL database.

Expected CSVs (with headers):
  - book.csv        : Isbn, Title
  - authors.csv     : Author_id, Name
  - book_authors.csv: Isbn, Author_id
  - borrower.csv    : Card_id, Bname, Address, Phone

Usage:
  python load_data.py \
    --host localhost \
    --port 3306 \
    --user root \
    --password yourpassword \
    --database library \
    --csvdir ./etl/output
"""

import argparse
import csv
import os
import sys
from typing import List, Tuple

import mysql.connector
from mysql.connector import Error

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import config


def get_connection(host: str, port: int, user: str, password: str, database: str):
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        return conn
    except Error as e:
        print(f"[ERROR] Could not connect to MySQL: {e}")
        sys.exit(1)


def truncate_tables(cursor):
    """
    Clear existing data so the load is repeatable.
    Order matters because of foreign keys.
    """
    print("[INFO] Truncating tables...")
    # Disable FK checks temporarily
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    cursor.execute("TRUNCATE TABLE BOOK_AUTHORS;")
    cursor.execute("TRUNCATE TABLE AUTHORS;")
    cursor.execute("TRUNCATE TABLE BOOK;")
    cursor.execute("TRUNCATE TABLE BORROWER;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")


def load_csv(
    cursor,
    table: str,
    csv_path: str,
    columns: List[str],
    batch_size: int = 1000,
):
    """
    Generic CSV loader using INSERT ... VALUES.
    - table: target table name
    - csv_path: path to CSV file
    - columns: list of column names in insert order
    """
    print(f"[INFO] Loading {csv_path} into {table}...")

    if not os.path.exists(csv_path):
        print(f"[WARN] File not found: {csv_path}. Skipping.")
        return

    placeholders = ", ".join(["%s"] * len(columns))
    col_list = ", ".join(columns)
    insert_sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: List[Tuple] = []
        for row in reader:
            # Build a tuple in the correct column order
            values = tuple(row[col] for col in columns)
            rows.append(values)

            # Insert in batches for performance
            if len(rows) >= batch_size:
                cursor.executemany(insert_sql, rows)
                rows.clear()

        # Insert any remaining rows
        if rows:
            cursor.executemany(insert_sql, rows)

    print(f"[INFO] Finished loading {table} from {csv_path}.")


def main():
    parser = argparse.ArgumentParser(description="Load normalized CSV data into MySQL.")
    parser.add_argument("--host", default=config.DB_HOST)
    parser.add_argument("--port", type=int, default=config.DB_PORT)
    parser.add_argument("--user", default=config.DB_USER)
    parser.add_argument("--password", default=config.DB_PASSWORD)
    parser.add_argument("--database", default=config.DB_NAME)
    parser.add_argument(
        "--csvdir",
        default="./etl/output",
        help="Directory containing book.csv, authors.csv, book_authors.csv, borrower.csv",
    )

    args = parser.parse_args()

    # Build CSV paths
    book_csv = os.path.join(args.csvdir, "book.csv")
    authors_csv = os.path.join(args.csvdir, "authors.csv")
    book_authors_csv = os.path.join(args.csvdir, "book_authors.csv")
    borrower_csv = os.path.join(args.csvdir, "borrower.csv")

    conn = get_connection(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database,
    )

    try:
        cursor = conn.cursor()

        # Optional: clear tables first so this is repeatable
        truncate_tables(cursor)

        # Load in dependency-safe order:
        # 1) BOOK, 2) AUTHORS, 3) BOOK_AUTHORS, 4) BORROWER
        load_csv(
            cursor,
            table="BOOK",
            csv_path=book_csv,
            columns=["Isbn", "Title"],
        )
        load_csv(
            cursor,
            table="AUTHORS",
            csv_path=authors_csv,
            columns=["Author_id", "Name"],
        )
        load_csv(
            cursor,
            table="BOOK_AUTHORS",
            csv_path=book_authors_csv,
            columns=["Isbn", "Author_id"],
        )
        load_csv(
            cursor,
            table="BORROWER",
            csv_path=borrower_csv,
            columns=["Card_id", "Bname", "Address", "Phone", "Ssn"],
        )

        conn.commit()
        print("[INFO] All data loaded and committed successfully.")

    except Error as e:
        print(f"[ERROR] MySQL error during load: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()
