-- Native PostgreSQL local training migration v2, not deployable Supabase SQL.
BEGIN;
SET LOCAL lock_timeout = '3s';
ALTER TABLE lab.stock ADD CONSTRAINT stock_max CHECK (remaining <= 10) NOT VALID;
ALTER TABLE lab.stock VALIDATE CONSTRAINT stock_max;
ALTER TABLE lab.drafts ADD COLUMN label text NOT NULL DEFAULT '';
ALTER TABLE lab.drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab.stock ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab.receipts ENABLE ROW LEVEL SECURITY;
ALTER TABLE lab.drafts FORCE ROW LEVEL SECURITY;
ALTER TABLE lab.stock FORCE ROW LEVEL SECURITY;
ALTER TABLE lab.receipts FORCE ROW LEVEL SECURITY;
REVOKE ALL ON ALL TABLES IN SCHEMA lab FROM PUBLIC,lab_member,lab_anon,lab_writer;
GRANT USAGE ON SCHEMA lab TO lab_member,lab_anon,lab_writer;
GRANT SELECT, INSERT ON lab.drafts TO lab_member;
GRANT UPDATE (body,label) ON lab.drafts TO lab_member;
GRANT SELECT ON lab.stock,lab.receipts TO lab_member;
CREATE POLICY draft_read ON lab.drafts FOR SELECT TO lab_member
 USING (owner = session_user);
CREATE POLICY draft_insert ON lab.drafts FOR INSERT TO lab_member
 WITH CHECK (owner = session_user);
CREATE POLICY draft_update ON lab.drafts FOR UPDATE TO lab_member
 USING (owner = session_user) WITH CHECK (owner = session_user);
CREATE POLICY stock_read ON lab.stock FOR SELECT TO lab_member
 USING (owner = session_user);
CREATE POLICY receipt_read ON lab.receipts FOR SELECT TO lab_member
 USING (owner = session_user);
-- The writer is a separately trusted backend DB identity, not a browser role.
GRANT SELECT, UPDATE(remaining) ON lab.stock TO lab_writer;
GRANT SELECT, INSERT ON lab.receipts TO lab_writer;
CREATE POLICY writer_stock_read ON lab.stock FOR SELECT TO lab_writer USING (true);
CREATE POLICY writer_stock_update ON lab.stock FOR UPDATE TO lab_writer USING (true) WITH CHECK (true);
CREATE POLICY writer_receipt_read ON lab.receipts FOR SELECT TO lab_writer USING (true);
CREATE POLICY writer_receipt_insert ON lab.receipts FOR INSERT TO lab_writer WITH CHECK (true);
CREATE VIEW lab.draft_view WITH (security_invoker = true) AS
 SELECT owner,id,body,label FROM lab.drafts;
REVOKE ALL ON lab.draft_view FROM PUBLIC;
GRANT SELECT ON lab.draft_view TO lab_member;
CREATE FUNCTION lab.reserve(p_owner name,p_token text,p_qty integer)
RETURNS text LANGUAGE plpgsql SECURITY INVOKER SET search_path = pg_catalog AS $$
DECLARE available integer; prior_qty integer; decision text;
BEGIN
 IF p_owner IS NULL OR p_token IS NULL OR length(p_token) NOT BETWEEN 1 AND 64
    OR p_qty IS NULL OR p_qty NOT BETWEEN 1 AND 10 THEN
    RAISE EXCEPTION 'invalid reservation' USING ERRCODE='22023';
 END IF;
 -- Serialize all operations for one owner before checking durable token receipt.
 SELECT remaining INTO available FROM lab.stock WHERE owner=p_owner FOR UPDATE;
 IF NOT FOUND THEN RAISE EXCEPTION 'unknown owner' USING ERRCODE='22023'; END IF;
 SELECT qty,outcome INTO prior_qty,decision FROM lab.receipts WHERE owner=p_owner AND token=p_token;
 IF FOUND THEN
    IF prior_qty<>p_qty THEN RAISE EXCEPTION 'token conflict' USING ERRCODE='22023'; END IF;
    RETURN decision;
 END IF;
 IF available>=p_qty THEN
    UPDATE lab.stock SET remaining=remaining-p_qty WHERE owner=p_owner;
    decision:='RESERVED';
 ELSE
    decision:='INSUFFICIENT';
 END IF;
 INSERT INTO lab.receipts VALUES(p_owner,p_token,p_qty,decision);
 RETURN decision;
END;
$$;
REVOKE ALL ON FUNCTION lab.reserve(name,text,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION lab.reserve(name,text,integer) TO lab_writer;
COMMIT;
