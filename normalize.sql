SET search_path TO sandbox;
/*
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** 
*** *** *** *** *** companies table *** *** *** *** *** *** *** *** ***
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** 
*/

DROP TABLE IF EXISTS tmp_os_cb_companies;
SELECT
    DISTINCT company_name, company_permalink
INTO TEMP tmp_os_cb_companies
FROM
    os_cb_deals
ORDER BY 1,2;

DROP TABLE IF EXISTS os_cb_companies;
CREATE TABLE os_cb_companies (
        id serial,
        name varchar,
        permalink text
);

INSERT INTO os_cb_companies (name, permalink) (
    SELECT company_name, company_permalink FROM tmp_os_cb_companies
);

DROP TABLE IF EXISTS tmp_os_cb_companies;

/*
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** 
*** *** *** *** *** Deals Table *** *** *** *** *** *** *** *** *** ***
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** 
*/

DROP TABLE IF EXISTS tmp_duplicate_companies;
SELECT
    a.id AS a_id
    , b.id AS b_id 
    , a.name AS a_name
    , b.name AS b_name
    , a.permalink AS a_permalink
    , b.permalink AS b_permalink
INTO TEMP tmp_duplicate_companies
FROM
    os_cb_companies a
    INNER JOIN os_cb_companies b
    ON a.name = b.name
    AND a.id != b.id
;

DROP TABLE IF EXISTS tmp_os_cb_deals;
SELECT DISTINCT 
    cb_deal_id
    , deal_currency_code
    , deal_date
    , deal_day
    , deal_month
    , deal_year
    , deal_amount
    , deal_round
    , company_permalink
    , company_name
INTO TEMP tmp_os_cb_deals
FROM
    os_cb_deals
WHERE
    cb_deal_id IS NOT NULL
    AND company_name NOT IN (
        SELECT a_name AS name FROM tmp_duplicate_companies
        UNION ALL
        SELECT b_name AS name FROM tmp_duplicate_companies
    );


DROP TABLE IF EXISTS os_cb_funding_rounds;

CREATE TABLE os_cb_funding_rounds (
        id serial,
        company_id integer
        , cb_deal_id varchar
        , deal_currency_code varchar
        , deal_date timestamp without time zone
        , deal_day integer
        , deal_month integer
        , deal_year integer
        , deal_amount FLOAT
        , deal_round varchar
);


INSERT INTO os_cb_funding_rounds (company_id, cb_deal_id, deal_currency_code, deal_date, deal_day, deal_month, deal_year, deal_amount, deal_round) (
    SELECT 
        company_id
        , cb_deal_id
        , deal_currency_code
        , deal_date
        , deal_day
        , deal_month
        , deal_year
        , deal_amount
        , deal_round
    FROM (
    SELECT
        co.id AS company_id
        , de.*
        
    FROM
        tmp_os_cb_deals de
        INNER JOIN os_cb_companies co
        ON co.name = de.company_name
    ) q
);

/*
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** ** 
*** *** *** *** *** Participants Table *** *** *** *** *** *** *** *** *** 
*** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** *** **
*/

DROP TABLE IF EXISTS tmp_participants;
SELECT
    DISTINCT participant_name
    , participant_permalink
    , participant_type
INTO TEMP tmp_participants
FROM
    os_cb_deals
WHERE
    (participant_name IS NOT NULL
     OR participant_permalink IS NOT NULL
     OR participant_type IS NOT NULL)
;

DROP TABLE IF EXISTS os_cb_participants;
CREATE TABLE os_cb_participants (
        id serial,
        name varchar,
        permalink text,
        type text
);

INSERT INTO os_cb_participants (name, permalink, type) (
    SELECT participant_name, participant_permalink, participant_type FROM tmp_participants
    ORDER BY participant_name
);

DROP TABLE IF EXISTS tmp_os_deal_participants;
SELECT 
    DISTINCT
    company_id
    , funding_round_id
    , participant_id
INTO TEMP tmp_os_deal_participants
FROM  (
    SELECT
        raw.company_name
        , raw.participant_name
        , raw.cb_deal_id
        , raw.deal_round
        , pa.id AS participant_id
        , co.id AS company_id
        , fu.id AS funding_round_id

    FROM
        os_cb_deals raw
        
        INNER JOIN os_cb_companies co
        ON co.name = raw.company_name

        INNER JOIN os_cb_funding_rounds fu
        ON fu.company_id = co.id

        LEFT JOIN os_cb_participants pa
        ON pa.name = raw.participant_name
    ORDER BY 1 
) q;

DROP TABLE IF EXISTS os_cb_funding_round_participants;
CREATE TABLE os_cb_funding_round_participants (
        id serial,
        company_id integer,
        funding_round_id integer,
        participant_id integer
);
INSERT INTO os_cb_funding_round_participants (company_id, funding_round_id, participant_id) (
    SELECT  
        co.id AS company_id
        , deals.id AS funding_round_id
        , pa.id AS participant_id
    FROM
        os_cb_companies co
        INNER JOIN tmp_os_deal_participants ref
            ON ref.company_id = co.id
        INNER JOIN os_cb_funding_rounds deals
            ON deals.company_id = co.id
        INNER JOIN os_cb_participants pa
            ON pa.id = ref.participant_id
            AND deals.id = ref.funding_round_id
            AND NOT pa.permalink~*E'.*(deleted).*'
) ;

DROP TABLE tmp_os_deal_participants;

-- select
--     fr.id AS funding_round_id
--     , co.name
--     , fr.deal_date AS date
--     , fr.deal_round AS round
--     , fr.deal_amount AS amount
--     , pa.name
--     , sum(1)
-- FROM
--     os_cb_companies co
--     INNER JOIN os_cb_funding_rounds fr
--         ON fr.company_id = co.id

--     INNER JOIN os_cb_funding_round_participants frp
--         ON frp.funding_round_id = fr.id
--         AND frp.company_id = co.id

--     LEFT JOIN os_cb_participants pa
--         ON pa.id = frp.participant_id

-- WHERE
--     co.name = 'OnDeck'
-- GROUP BY 1,2,3,4,5,6
-- ORDER BY 1;
