-- Small sample dataset for development & testing

USE library;

-- ===========================================
-- SAMPLE BOOKS
-- ===========================================
INSERT INTO BOOK (Isbn, Title) VALUES
    ('0000000001', 'Database System Concepts'),
    ('0000000002', 'Introduction to Algorithms'),
    ('0000000003', 'Operating Systems Design'),
    ('0000000004', 'Computer Networks');

-- ===========================================
-- SAMPLE AUTHORS
-- ===========================================
INSERT INTO AUTHORS (Author_id, Name) VALUES
    (1, 'Abraham Silberschatz'),
    (2, 'Henry F. Korth'),
    (3, 'S. Sudarshan'),
    (4, 'Thomas H. Cormen'),
    (5, 'Charles E. Leiserson'),
    (6, 'Ronald L. Rivest'),
    (7, 'Clifford Stein'),
    (8, 'Andrew S. Tanenbaum');

-- ===========================================
-- SAMPLE BOOK_AUTHORS LINKS
-- ===========================================
INSERT INTO BOOK_AUTHORS (Isbn, Author_id) VALUES
    -- Database System Concepts
    ('0000000001', 1),
    ('0000000001', 2),
    ('0000000001', 3),

    -- Introduction to Algorithms
    ('0000000002', 4),
    ('0000000002', 5),
    ('0000000002', 6),
    ('0000000002', 7),

    -- Operating Systems Design
    ('0000000003', 1),

    -- Computer Networks
    ('0000000004', 8);

-- ===========================================
-- SAMPLE BORROWERS
-- Card_id format consistent with what your group discussed (ID + zero-padded int)
-- ===========================================
INSERT INTO BORROWER (Card_id, Ssn, Bname, Address, Phone) VALUES
    ('ID00001', '111111111', 'Alice Johnson',   '123 Maple St',      '555-111-1111'),
    ('ID00002', '222222222', 'Bob Smith',       '456 Oak Ave',       '555-222-2222'),
    ('ID00003', '333333333', 'Charlie Nguyen',  '789 Pine Blvd',     '555-333-3333');

-- ===========================================
-- SAMPLE LOANS
-- Some are returned, some still out, some overdue.
-- Adjust dates as needed; they’re mainly for fines logic testing.
-- ===========================================

-- Alice checks out Database System Concepts (returned on time)
INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in) VALUES
    ('0000000001', 'ID00001', '2025-01-01', '2025-01-15', '2025-01-10');

-- Bob checks out Introduction to Algorithms (returned late)
INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in) VALUES
    ('0000000002', 'ID00002', '2025-01-01', '2025-01-15', '2025-01-25');

-- Charlie checks out Operating Systems Design (still out, overdue)
INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in) VALUES
    ('0000000003', 'ID00003', '2025-01-10', '2025-01-24', NULL);

-- Alice checks out Computer Networks (still within due date, not overdue in this example)
INSERT INTO BOOK_LOANS (Isbn, Card_id, Date_out, Due_date, Date_in) VALUES
    ('0000000004', 'ID00001', '2025-01-20', '2025-02-03', NULL);

-- ===========================================
-- SAMPLE FINES
-- You can either let your update_fines() function generate these,
-- or pre-populate a couple to test pay_fines logic.
-- Here we show one returned-late loan with a fine and one unpaid fine.
-- ===========================================

-- Assume Bob's late return (Loan_id 2) has a fine of $2.50, unpaid
-- (you may need to check the actual auto-increment IDs if you rerun data)
INSERT INTO FINES (Loan_id, Fine_amt, Paid) VALUES
    (2, 2.50, 0);
