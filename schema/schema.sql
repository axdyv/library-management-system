-- CS 4347 Library Management System - Database Schema
-- DBMS: MySQL

CREATE DATABASE IF NOT EXISTS library;
USE library;

-- Drop tables if they already exist
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS FINES;
DROP TABLE IF EXISTS BOOK_LOANS;
DROP TABLE IF EXISTS BOOK_AUTHORS;
DROP TABLE IF EXISTS AUTHORS;
DROP TABLE IF EXISTS BORROWER;
DROP TABLE IF EXISTS BOOK;

SET FOREIGN_KEY_CHECKS = 1;

-- ===========================================
-- BOOK: basic book info (normalized from books.csv)
-- ===========================================
CREATE TABLE BOOK (
    Isbn        VARCHAR(10)  NOT NULL,
    Title       VARCHAR(255) NOT NULL,
    -- NEED TO ADD MORE ATTRIBUTES (e.g., publisher, year, etc.)
    PRIMARY KEY (Isbn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Index to help title-based search
CREATE INDEX idx_book_title ON BOOK (Title);

-- ===========================================
-- AUTHORS: unique authors
-- ===========================================
CREATE TABLE AUTHORS (
    Author_id   INT          NOT NULL,
    Name        VARCHAR(255) NOT NULL,
    PRIMARY KEY (Author_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Index to help author-name search
CREATE INDEX idx_authors_name ON AUTHORS (Name);

-- ===========================================
-- BOOK_AUTHORS: M:N relationship between books and authors
-- ===========================================
CREATE TABLE BOOK_AUTHORS (
    Isbn        VARCHAR(10) NOT NULL,
    Author_id   INT         NOT NULL,
    PRIMARY KEY (Isbn, Author_id),
    CONSTRAINT fk_book_authors_book
        FOREIGN KEY (Isbn) REFERENCES BOOK (Isbn)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_book_authors_author
        FOREIGN KEY (Author_id) REFERENCES AUTHORS (Author_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- BORROWER: people with library cards
-- (normalized from borrowers.csv)
-- ===========================================
CREATE TABLE BORROWER (
    Card_id     VARCHAR(20)  NOT NULL,
    Ssn         CHAR(9)      NOT NULL,
    Bname       VARCHAR(255) NOT NULL,
    Address     VARCHAR(255) NOT NULL,
    Phone       VARCHAR(20),
    PRIMARY KEY (Card_id),
    UNIQUE KEY uq_borrower_ssn (Ssn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- BOOK_LOANS: each instance of checking out a book
-- ===========================================
CREATE TABLE BOOK_LOANS (
    Loan_id     INT          NOT NULL AUTO_INCREMENT,
    Isbn        VARCHAR(10)  NOT NULL,
    Card_id     VARCHAR(20)  NOT NULL,
    Date_out    DATE         NOT NULL,
    Due_date    DATE         NOT NULL,
    Date_in     DATE         DEFAULT NULL,
    PRIMARY KEY (Loan_id),
    KEY idx_loans_isbn (Isbn),
    KEY idx_loans_card (Card_id),
    CONSTRAINT fk_book_loans_book
        FOREIGN KEY (Isbn) REFERENCES BOOK (Isbn)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_book_loans_borrower
        FOREIGN KEY (Card_id) REFERENCES BORROWER (Card_id)
        ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ===========================================
-- FINES: one row per loan that has (or had) a fine
-- ===========================================
CREATE TABLE FINES (
    Loan_id     INT           NOT NULL,
    Fine_amt    DECIMAL(6,2)  NOT NULL,
    Paid        TINYINT(1)    NOT NULL DEFAULT 0,
    PRIMARY KEY (Loan_id),
    CONSTRAINT fk_fines_loan
        FOREIGN KEY (Loan_id) REFERENCES BOOK_LOANS (Loan_id)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
