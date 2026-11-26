-- Native PostgreSQL local training migration v3. Preserve v2 history.
-- Existing receipts and ACL remain intact; only reserve implementation changes.
BEGIN;
SET LOCAL lock_timeout = '3s';
CREATE OR REPLACE FUNCTION lab.reserve(p_owner name,p_token text,p_qty integer)
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
    -- A newly persisted denial changes the owner decision stream too.
    -- Publish a stock row version so a stale REPEATABLE READ snapshot
    -- fails with 40001 instead of a hidden receipt causing 23505.
    -- No logical inventory change; replays above do not write a new version.
    UPDATE lab.stock SET remaining=remaining WHERE owner=p_owner;
    decision:='INSUFFICIENT';
 END IF;
 INSERT INTO lab.receipts VALUES(p_owner,p_token,p_qty,decision);
 RETURN decision;
END;
$$;
COMMIT;
