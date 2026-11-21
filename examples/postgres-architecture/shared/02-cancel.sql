-- Add reversible business lifecycle by forward-only schema migration.
-- Existing reservations and denied decisions retain their original outcome.
BEGIN;
SET LOCAL lock_timeout='3s';
ALTER TABLE sharedlab.bookings ADD COLUMN active boolean NOT NULL DEFAULT true;
ALTER TABLE sharedlab.decisions DROP CONSTRAINT decision_shape;
ALTER TABLE sharedlab.decisions ADD CONSTRAINT decision_shape CHECK(
 (operation='reserve' AND target=token AND qty IS NOT NULL AND qty>0 AND outcome IN ('RESERVED','INSUFFICIENT'))
 OR (operation='cancel' AND qty IS NULL AND outcome IN ('CANCELLED','NOT_ACTIVE')));
GRANT UPDATE(active) ON sharedlab.bookings TO lab_shared_exec;
CREATE POLICY exec_booking_update ON sharedlab.bookings FOR UPDATE TO lab_shared_exec
 USING(owner=session_user) WITH CHECK(owner=session_user);
CREATE FUNCTION sharedlab.cancel(p_token text,p_target text)
RETURNS text LANGUAGE plpgsql SECURITY DEFINER
SET search_path=pg_catalog,pg_temp AS $$
DECLARE actor name:=session_user; available integer; prior sharedlab.decisions%ROWTYPE; released integer; result text;
BEGIN
 IF NOT pg_has_role(actor,'lab_member','MEMBER') THEN
    RAISE EXCEPTION 'not a member' USING ERRCODE='42501';
 END IF;
 IF p_token IS NULL OR length(p_token) NOT BETWEEN 1 AND 64
    OR p_target IS NULL OR length(p_target) NOT BETWEEN 1 AND 64 THEN
    RAISE EXCEPTION 'invalid request' USING ERRCODE='22023';
 END IF;
 SELECT remaining INTO STRICT available FROM sharedlab.pool WHERE id=1 FOR UPDATE;
 SELECT * INTO prior FROM sharedlab.decisions WHERE owner=actor AND token=p_token;
 IF FOUND THEN
    IF prior.operation<>'cancel' OR prior.target IS DISTINCT FROM p_target THEN
       RAISE EXCEPTION 'token conflict' USING ERRCODE='22023';
    END IF;
    RETURN prior.outcome;
 END IF;
 UPDATE sharedlab.bookings SET active=false WHERE owner=actor AND token=p_target AND active
 RETURNING qty INTO released;
 IF FOUND THEN result:='CANCELLED'; ELSE result:='NOT_ACTIVE'; released:=0; END IF;
 UPDATE sharedlab.pool SET remaining=remaining+released,decision_version=decision_version+1 WHERE id=1;
 INSERT INTO sharedlab.decisions(owner,token,operation,target,qty,outcome)
 VALUES(actor,p_token,'cancel',p_target,NULL,result);
 RETURN result;
END;
$$;
ALTER FUNCTION sharedlab.cancel(text,text) OWNER TO lab_shared_exec;
REVOKE ALL ON FUNCTION sharedlab.cancel(text,text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION sharedlab.cancel(text,text) TO lab_member;
COMMIT;
