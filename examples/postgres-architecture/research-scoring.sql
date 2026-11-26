-- TD004-SQL-HOMEWORK-01: synthetic training ONLY; no real scale or research policy.
-- Requires isolated training cluster lab_* roles. Never run against production.
CREATE SCHEMA scorelab;
REVOKE ALL ON SCHEMA scorelab FROM PUBLIC;
CREATE TABLE scorelab.study(id integer PRIMARY KEY, owner name NOT NULL);
CREATE TABLE scorelab.participant(study_id integer REFERENCES scorelab.study,
    person integer, PRIMARY KEY(study_id,person));
CREATE TABLE scorelab.rule(version integer PRIMARY KEY, reverse_weight integer NOT NULL
    CHECK(reverse_weight IN (1,2)));
CREATE TABLE scorelab.visit(study_id integer, person integer, wave integer CHECK(wave>0),
    attempt integer CHECK(attempt>0), version integer NOT NULL REFERENCES scorelab.rule,
    submitted boolean NOT NULL DEFAULT false,
    PRIMARY KEY(study_id,person,wave,attempt),
    FOREIGN KEY(study_id,person) REFERENCES scorelab.participant);
CREATE TABLE scorelab.response(study_id integer, person integer, wave integer,
    attempt integer, item integer CHECK(item BETWEEN 1 AND 3),
    value integer CHECK(value BETWEEN 0 AND 4),
    PRIMARY KEY(study_id,person,wave,attempt,item),
    FOREIGN KEY(study_id,person,wave,attempt) REFERENCES scorelab.visit);
CREATE TABLE scorelab.submission(study_id integer,person integer,wave integer,attempt integer,
    actor name NOT NULL,
    PRIMARY KEY(study_id,person,wave,attempt),
    FOREIGN KEY(study_id,person,wave,attempt) REFERENCES scorelab.visit);

-- Rule publication and visit planning are trusted fixture/admin actions.
-- Existing rules/visit identities remain pinned by policy; app roles cannot edit them.
INSERT INTO scorelab.study VALUES(1,'lab_alice'),(2,'lab_bob');
INSERT INTO scorelab.participant VALUES(1,1),(1,2),(1,3),(1,4),(2,1);
INSERT INTO scorelab.rule VALUES(1,1);
INSERT INTO scorelab.visit(study_id,person,wave,attempt,version)
VALUES(1,1,1,1,1),(1,1,1,2,1),(1,2,1,1,1),(1,3,1,1,1),(1,4,1,1,1),(2,1,1,1,1);

-- One planned visit/attempt per output row. Only complete forms have totals.
-- Separate explicit missing answers from no submitted form, and keep zero.
CREATE VIEW scorelab.report WITH (security_barrier=true) AS
 SELECT v.study_id,v.person,v.wave,v.attempt,v.version,v.submitted,
        count(r.item) AS recorded,count(r.value) AS valid,
        CASE WHEN v.submitted AND count(r.item)=3 AND count(r.value)=3
             THEN sum(CASE WHEN r.item=2 THEN (4-r.value)*m.reverse_weight ELSE r.value END)
             ELSE NULL END AS total
 FROM scorelab.visit v
 JOIN scorelab.study s ON s.id=v.study_id
 JOIN scorelab.rule m ON m.version=v.version
 LEFT JOIN scorelab.response r USING(study_id,person,wave,attempt)
 WHERE s.owner=session_user
 GROUP BY v.study_id,v.person,v.wave,v.attempt,v.version,v.submitted,m.reverse_weight;
-- Aggregation never pools different calculation versions.
CREATE VIEW scorelab.summary WITH (security_barrier=true) AS
 SELECT study_id,wave,version,count(*) AS planned,count(*) FILTER(WHERE submitted) AS submitted,
        count(total) AS complete,sum(total) AS total_sum
 FROM scorelab.report GROUP BY study_id,wave,version;

CREATE FUNCTION scorelab.submit(p_study integer,p_person integer,p_wave integer,
    p_attempt integer,p_answers integer[]) RETURNS text
 LANGUAGE plpgsql VOLATILE SECURITY DEFINER SET search_path=pg_catalog,pg_temp AS $$
 DECLARE done boolean;
 BEGIN
   SELECT v.submitted INTO done FROM scorelab.visit v
     JOIN scorelab.study s ON s.id=v.study_id
     WHERE v.study_id=p_study AND v.person=p_person AND v.wave=p_wave
       AND v.attempt=p_attempt AND s.owner=session_user
     FOR UPDATE OF v;
   IF NOT FOUND THEN RAISE EXCEPTION 'visit unavailable' USING ERRCODE='42501'; END IF;
   IF done THEN RETURN 'ALREADY_FINAL'; END IF;
   IF array_ndims(p_answers) IS DISTINCT FROM 1 OR cardinality(p_answers) IS DISTINCT FROM 3
       OR array_lower(p_answers,1) IS DISTINCT FROM 1 THEN
     RAISE EXCEPTION 'three answers required' USING ERRCODE='22023';
   END IF;
   -- Deliberately update state before the constrained insert; a bad answer must
   -- undo the prior state change too, not leave a finalized partial form.
   UPDATE scorelab.visit SET submitted=true WHERE study_id=p_study AND person=p_person
       AND wave=p_wave AND attempt=p_attempt;
   INSERT INTO scorelab.response(study_id,person,wave,attempt,item,value)
     SELECT p_study,p_person,p_wave,p_attempt,ordinality::integer,val
       FROM unnest(p_answers) WITH ORDINALITY AS q(val,ordinality);
   INSERT INTO scorelab.submission VALUES(p_study,p_person,p_wave,p_attempt,session_user);
   RETURN 'SUBMITTED';
 END;
 $$;
-- Reuse a non-superuser fixture role as definer, not as an application login.
GRANT USAGE,CREATE ON SCHEMA scorelab TO lab_writer;
GRANT SELECT ON scorelab.study,scorelab.visit TO lab_writer;
GRANT UPDATE(submitted) ON scorelab.visit TO lab_writer;
GRANT INSERT ON scorelab.response,scorelab.submission TO lab_writer;
ALTER FUNCTION scorelab.submit(integer,integer,integer,integer,integer[]) OWNER TO lab_writer;
REVOKE CREATE ON SCHEMA scorelab FROM lab_writer;
REVOKE ALL ON FUNCTION scorelab.submit(integer,integer,integer,integer,integer[]) FROM PUBLIC;
GRANT USAGE ON SCHEMA scorelab TO lab_member;
GRANT EXECUTE ON FUNCTION scorelab.submit(integer,integer,integer,integer,integer[]) TO lab_member;
GRANT SELECT ON scorelab.report,scorelab.summary TO lab_member;
