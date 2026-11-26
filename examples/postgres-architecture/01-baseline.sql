-- Isolated native PostgreSQL training fixture ONLY. Not a Supabase migration.
-- Run only inside the disposable cluster created by tests/test_postgres_architecture.py.
BEGIN;
CREATE SCHEMA lab;
REVOKE ALL ON SCHEMA lab FROM PUBLIC;
CREATE TABLE lab.drafts (
 owner name NOT NULL, id text NOT NULL, body text NOT NULL,
 PRIMARY KEY(owner,id)
);
CREATE TABLE lab.stock (
 owner name PRIMARY KEY, remaining integer NOT NULL CHECK (remaining >= 0)
);
CREATE TABLE lab.receipts (
 owner name NOT NULL REFERENCES lab.stock(owner),
 token text NOT NULL, qty integer NOT NULL CHECK(qty BETWEEN 1 AND 10),
 outcome text NOT NULL CHECK(outcome IN ('RESERVED','INSUFFICIENT')),
 PRIMARY KEY(owner,token)
);
INSERT INTO lab.drafts VALUES ('lab_alice','draft','A'),('lab_bob','draft','B');
INSERT INTO lab.stock VALUES ('lab_alice',10),('lab_bob',10);
COMMIT;
