-- Native PostgreSQL training only. Disposable lab cluster, not a cloud migration.
-- Precondition: trusted lab administrator and fresh lab_shared_exec NOLOGIN role.
BEGIN;
SET LOCAL lock_timeout='3s';
CREATE SCHEMA sharedlab;
REVOKE ALL ON SCHEMA sharedlab FROM PUBLIC;
GRANT USAGE ON SCHEMA sharedlab TO lab_member, lab_shared_exec;
CREATE TABLE sharedlab.pool (
 id integer PRIMARY KEY CHECK(id=1),
 capacity integer NOT NULL CHECK(capacity>0),
 remaining integer NOT NULL CHECK(remaining BETWEEN 0 AND capacity),
 decision_version bigint NOT NULL DEFAULT 0 CHECK(decision_version>=0)
);
CREATE TABLE sharedlab.bookings (
 owner name NOT NULL, token text NOT NULL CHECK(length(token) BETWEEN 1 AND 64),
 qty integer NOT NULL CHECK(qty>0), PRIMARY KEY(owner,token)
);
CREATE TABLE sharedlab.decisions (
 owner name NOT NULL, token text NOT NULL CHECK(length(token) BETWEEN 1 AND 64),
 operation text NOT NULL, target text NOT NULL CHECK(length(target) BETWEEN 1 AND 64),
 qty integer, outcome text NOT NULL, PRIMARY KEY(owner,token),
 CONSTRAINT decision_shape CHECK(
   operation='reserve' AND target=token AND qty IS NOT NULL AND qty>0
   AND outcome IN ('RESERVED','INSUFFICIENT'))
);
INSERT INTO sharedlab.pool(id,capacity,remaining) VALUES(1,10,10);
REVOKE ALL ON ALL TABLES IN SCHEMA sharedlab FROM PUBLIC,lab_member,lab_shared_exec;
ALTER TABLE sharedlab.pool ENABLE ROW LEVEL SECURITY;
ALTER TABLE sharedlab.pool FORCE ROW LEVEL SECURITY;
ALTER TABLE sharedlab.bookings ENABLE ROW LEVEL SECURITY;
ALTER TABLE sharedlab.bookings FORCE ROW LEVEL SECURITY;
ALTER TABLE sharedlab.decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sharedlab.decisions FORCE ROW LEVEL SECURITY;
GRANT SELECT ON sharedlab.pool,sharedlab.bookings,sharedlab.decisions TO lab_member,lab_shared_exec;
GRANT UPDATE(remaining,decision_version) ON sharedlab.pool TO lab_shared_exec;
GRANT INSERT ON sharedlab.bookings,sharedlab.decisions TO lab_shared_exec;
CREATE POLICY member_pool ON sharedlab.pool FOR SELECT TO lab_member USING (true);
CREATE POLICY member_booking ON sharedlab.bookings FOR SELECT TO lab_member USING(owner=session_user);
CREATE POLICY member_decision ON sharedlab.decisions FOR SELECT TO lab_member USING(owner=session_user);
CREATE POLICY exec_pool_read ON sharedlab.pool FOR SELECT TO lab_shared_exec USING(true);
CREATE POLICY exec_pool_update ON sharedlab.pool FOR UPDATE TO lab_shared_exec USING(true) WITH CHECK(true);
CREATE POLICY exec_booking_read ON sharedlab.bookings FOR SELECT TO lab_shared_exec USING(owner=session_user);
CREATE POLICY exec_booking_insert ON sharedlab.bookings FOR INSERT TO lab_shared_exec WITH CHECK(owner=session_user);
CREATE POLICY exec_decision_read ON sharedlab.decisions FOR SELECT TO lab_shared_exec USING(owner=session_user);
CREATE POLICY exec_decision_insert ON sharedlab.decisions FOR INSERT TO lab_shared_exec WITH CHECK(owner=session_user);

CREATE FUNCTION sharedlab.reserve(p_token text,p_qty integer)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,pg_temp AS $$
DECLARE actor name:=session_user; available integer; max_qty integer; prior sharedlab.decisions%ROWTYPE; result text;
BEGIN
 IF NOT pg_has_role(actor,'lab_member','MEMBER') THEN
    RAISE EXCEPTION 'not a member' USING ERRCODE='42501';
 END IF;
 IF p_token IS NULL OR length(p_token) NOT BETWEEN 1 AND 64 OR p_qty IS NULL OR p_qty<1 THEN
    RAISE EXCEPTION 'invalid request' USING ERRCODE='22023';
 END IF;
 SELECT remaining,capacity INTO STRICT available,max_qty FROM sharedlab.pool WHERE id=1 FOR UPDATE;
 IF p_qty>max_qty THEN RAISE EXCEPTION 'invalid quantity' USING ERRCODE='22023'; END IF;
 SELECT * INTO prior FROM sharedlab.decisions WHERE owner=actor AND token=p_token;
 IF FOUND THEN
    IF prior.operation<>'reserve' OR prior.qty IS DISTINCT FROM p_qty THEN
       RAISE EXCEPTION 'token conflict' USING ERRCODE='22023';
    END IF;
    RETURN prior.outcome;
 END IF;
 IF available>=p_qty THEN
    INSERT INTO sharedlab.bookings(owner,token,qty) VALUES(actor,p_token,p_qty);
    result:='RESERVED';
 ELSE
    result:='INSUFFICIENT';
 END IF;
 -- Every new decision, even denial, versions the same shared resource row.
 UPDATE sharedlab.pool SET remaining=remaining-CASE WHEN result='RESERVED' THEN p_qty ELSE 0 END,
    decision_version=decision_version+1 WHERE id=1;
 INSERT INTO sharedlab.decisions(owner,token,operation,target,qty,outcome)
 VALUES(actor,p_token,'reserve',p_token,p_qty,result);
 RETURN result;
END;
$$;
ALTER FUNCTION sharedlab.reserve(text,integer) OWNER TO lab_shared_exec;
REVOKE ALL ON FUNCTION sharedlab.reserve(text,integer) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sharedlab.reserve(text,integer) TO lab_member;
COMMIT;
