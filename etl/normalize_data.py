#!/usr/bin/env python3
"""
normalize_data.py
To run:
make sure python is installed (v3)
pip install pandas if the library isn't already installed
run this command in terminal:
python normalize_data.py --books [books_file.csv] --borrowers [borrowers_file.csv] --outdir [output]

Outputs:
  - book.csv (Isbn=ISBN10, Title)
  - authors.csv (Author_id, Name)
  - book_authors.csv (Isbn=ISBN10, Author_id)
  - borrower.csv (Card_id=ID0000id, Bname=First Last, Address="address, city, state", Phone=phone)
"""
import argparse
from pathlib import Path
import re
import pandas as pd


def normalize_whitespace(s):
    """
    Normalize whitespace in a string field.

    Parsing steps:
    - If the value is a pandas NA, return an empty string (treat missing as empty).
    - Convert the value to a string.
    - Collapse any sequence of whitespace (spaces, tabs, newlines) to a single space.
    - Trim leading and trailing whitespace.

    Input: any value (commonly a pandas series element).
    Output: a cleaned string with normalized whitespace (or empty string for NA).
    """
    if pd.isna(s):
        return ""
    return re.sub(r'\s+', ' ', str(s)).strip()


def title_case(s):
    """
    Normalize casing for a textual field (title-casing when appropriate).

    Parsing steps:
    - First normalize whitespace.
    - If the string is empty, return it as-is.
    - If the entire string is lower-case or upper-case, convert to title case
      (capitalizing words). Otherwise, assume the casing is already intentional
      and return the string unchanged.

    Input: string-like value.
    Output: string with adjusted title case where appropriate.
    """
    s = normalize_whitespace(s)
    if not s:
        return s
    return s.title() if (s.islower() or s.isupper()) else s


def split_authors(field):
        """
        Parse an authors field into a de-duplicated list of author names.

        Parsing steps:
        - Treat empty or NA fields as no authors (return empty list).
        - Convert the field to string and normalize common separators:
            - Replace instances of the word 'and' (case-insensitive, surrounded by whitespace)
                with a comma.
            - Replace ampersands '&' with commas.
        - Split the resulting string on common separators: semicolon, comma, or pipe.
        - For each part, normalize whitespace and apply `title_case` to make the name
            look consistent.
        - De-duplicate names in a case-insensitive way while preserving original order.

        Input: raw author field (string-like).
        Output: list of cleaned, unique author names.
        """
        if pd.isna(field) or not str(field).strip():
                return []
        raw = str(field)
        raw = re.sub(r'\s+(?i:and)\s+', ',', raw)
        raw = raw.replace('&', ',')
        parts = re.split(r'[;,|]', raw)
        names = [title_case(p) for p in parts if normalize_whitespace(p)]
        seen = set()
        out = []
        for n in names:
                key = n.lower()
                if key not in seen:
                        seen.add(key)
                        out.append(n)
        return out


def process_books(books_path: Path):
        """
        Read and normalize a books TSV file, and produce three tables:
            - book: unique books with ISBN10 and Title
            - authors: unique author id/name pairs
            - book_authors: many-to-many links between ISBN and author ids

        Parsing steps:
        - Read the input as a TSV (tab-separated) CSV with all columns as strings.
        - Normalize whitespace for every column value.
        - Filter out rows that lack an ISBN10 (we prefer ISBN10 as the canonical key).
        - Build the `book` table by selecting ISBN10 and Title, renaming ISBN10 -> Isbn,
            and dropping duplicate ISBNs.
        - For authors:
            - For each book row, take the raw Author field and pass it to `split_authors`.
            - Maintain a mapping from normalized author name (lowercase) to a generated
                integer Author_id to deduplicate authors across rows.
            - Collect rows for the `authors` table (Author_id, Name) and the link table
                `book_authors` (Isbn, Author_id).
            - De-duplicate links where the same (Isbn, Author_id) might appear multiple times.

        Input: Path to books TSV file.
        Output: tuple of pandas DataFrames: (book, authors, book_authors).
        """
        # TSV file
        bdf = pd.read_csv(books_path, dtype=str, sep='\t', keep_default_na=False)
        for col in bdf.columns:
                bdf[col] = bdf[col].map(normalize_whitespace)

        # Prefer ISBN10; drop rows missing ISBN10
        bdf = bdf[bdf['ISBN10'].astype(str).str.len() > 0].copy()

        # BOOK
        book = bdf[['ISBN10', 'Title']].copy()
        book.columns = ['Isbn', 'Title']
        book = book.drop_duplicates(subset=['Isbn']).reset_index(drop=True)

        # AUTHORS + BOOK_AUTHORS
        author_name_to_id = {}
        authors_rows = []
        book_authors_rows = []

        for _, row in bdf.iterrows():
                isbn = row['ISBN10']
                authors_raw = row.get('Author', '')
                names = split_authors(authors_raw)
                for name in names:
                        key = name.lower()
                        if key not in author_name_to_id:
                                author_id = len(author_name_to_id) + 1
                                author_name_to_id[key] = author_id
                                authors_rows.append((author_id, name))
                        aid = author_name_to_id[key]
                        book_authors_rows.append((isbn, aid))

        authors = pd.DataFrame(authors_rows, columns=['Author_id', 'Name']).sort_values('Author_id')
        book_authors = pd.DataFrame(book_authors_rows, columns=['Isbn', 'Author_id']).drop_duplicates()

        return book, authors, book_authors


def process_borrowers(path: Path):
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    for col in df.columns:
        df[col] = df[col].map(normalize_whitespace)

    # Compose fields
    df['Card_id'] = df['ID0000id']
    df['Bname'] = (df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')).str.strip().map(title_case)
    df['Address'] = (df['address'].fillna('') + ', ' + df['city'].fillna('') + ', ' + df['state'].fillna('')).str.strip(' ,')
    df['Phone'] = df['phone']
    df['Ssn'] = df['ssn'].str.replace('-', '', regex=False) #keeps Ssn as digits only

    out = df[['Card_id', 'Bname', 'Address', 'Phone', 'Ssn']].drop_duplicates(subset=['Card_id']).reset_index(drop=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--books', required=True)
    ap.add_argument('--borrowers', required=True)
    ap.add_argument('--outdir', default='.')
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    book, authors, book_authors = process_books(Path(args.books))
    borrower = process_borrowers(Path(args.borrowers))

    book.to_csv(outdir / 'book.csv', index=False)
    authors.to_csv(outdir / 'authors.csv', index=False)
    book_authors.to_csv(outdir / 'book_authors.csv', index=False)
    borrower.to_csv(outdir / 'borrower.csv', index=False)

    print(f"Wrote {len(book)} books, {len(authors)} authors, {len(book_authors)} links, {len(borrower)} borrowers to {outdir}")

if __name__ == "__main__":
    main()