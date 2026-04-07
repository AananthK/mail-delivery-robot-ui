--
-- PostgreSQL database dump
--

\restrict cVsTTD1NKeInGMXticdYqUNWJa7uopSag9I8UylYsP7yRmpflMa6s6Bq6GMgTvw

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY "public"."robot" DROP CONSTRAINT IF EXISTS "robot_next_room_fkey";
ALTER TABLE IF EXISTS ONLY "public"."robot_event_log" DROP CONSTRAINT IF EXISTS "robot_event_log_robot_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."robot_event_log" DROP CONSTRAINT IF EXISTS "robot_event_log_delivery_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."robot" DROP CONSTRAINT IF EXISTS "robot_current_room_fkey";
ALTER TABLE IF EXISTS ONLY "public"."message_log" DROP CONSTRAINT IF EXISTS "message_log_sender_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."message_log" DROP CONSTRAINT IF EXISTS "message_log_sender_robot_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."message_log" DROP CONSTRAINT IF EXISTS "message_log_recipient_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."message_log" DROP CONSTRAINT IF EXISTS "message_log_recipient_robot_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."message_log" DROP CONSTRAINT IF EXISTS "message_log_delivery_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."delivery" DROP CONSTRAINT IF EXISTS "delivery_room_number_fkey";
ALTER TABLE IF EXISTS ONLY "public"."delivery" DROP CONSTRAINT IF EXISTS "delivery_recipient_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."delivery" DROP CONSTRAINT IF EXISTS "delivery_assigned_robot_fkey";
ALTER TABLE IF EXISTS ONLY "public"."delivery" DROP CONSTRAINT IF EXISTS "delivery_admin_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."room" DROP CONSTRAINT IF EXISTS "room_pkey";
ALTER TABLE IF EXISTS ONLY "public"."robot" DROP CONSTRAINT IF EXISTS "robot_pkey";
ALTER TABLE IF EXISTS ONLY "public"."robot_event_log" DROP CONSTRAINT IF EXISTS "robot_event_log_pkey";
ALTER TABLE IF EXISTS ONLY "public"."message_log" DROP CONSTRAINT IF EXISTS "message_log_pkey";
ALTER TABLE IF EXISTS ONLY "public"."delivery" DROP CONSTRAINT IF EXISTS "delivery_pkey";
ALTER TABLE IF EXISTS ONLY "public"."account" DROP CONSTRAINT IF EXISTS "account_username_key";
ALTER TABLE IF EXISTS ONLY "public"."account" DROP CONSTRAINT IF EXISTS "account_pkey";
ALTER TABLE IF EXISTS ONLY "public"."account" DROP CONSTRAINT IF EXISTS "account_email_key";
ALTER TABLE IF EXISTS "public"."robot_event_log" ALTER COLUMN "event_id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."robot" ALTER COLUMN "robot_id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."message_log" ALTER COLUMN "message_id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."delivery" ALTER COLUMN "delivery_id" DROP DEFAULT;
ALTER TABLE IF EXISTS "public"."account" ALTER COLUMN "user_id" DROP DEFAULT;
DROP TABLE IF EXISTS "public"."room";
DROP SEQUENCE IF EXISTS "public"."robot_robot_id_seq";
DROP SEQUENCE IF EXISTS "public"."robot_event_log_event_id_seq";
DROP TABLE IF EXISTS "public"."robot_event_log";
DROP TABLE IF EXISTS "public"."robot";
DROP SEQUENCE IF EXISTS "public"."message_log_message_id_seq";
DROP TABLE IF EXISTS "public"."message_log";
DROP SEQUENCE IF EXISTS "public"."delivery_delivery_id_seq";
DROP TABLE IF EXISTS "public"."delivery";
DROP SEQUENCE IF EXISTS "public"."account_user_id_seq";
DROP TABLE IF EXISTS "public"."account";
--
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- Name: account; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."account" (
    "user_id" integer NOT NULL,
    "username" character varying(30) NOT NULL,
    "password_hash" character varying(255) NOT NULL,
    "first_name" character varying(20) NOT NULL,
    "last_name" character varying(20) NOT NULL,
    "user_role" character varying(5) NOT NULL,
    "email" character varying(50) NOT NULL,
    "phone_number" character varying(11),
    CONSTRAINT "account_user_role_check" CHECK ((("user_role")::"text" = ANY ((ARRAY['admin'::character varying, 'user'::character varying])::"text"[])))
);


--
-- Name: account_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."account_user_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: account_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."account_user_id_seq" OWNED BY "public"."account"."user_id";


--
-- Name: delivery; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."delivery" (
    "delivery_id" integer NOT NULL,
    "admin_user_id" integer NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "last_updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "sender_name" character varying(30) NOT NULL,
    "sender_address" character varying(50) NOT NULL,
    "sender_phone" character varying(11),
    "sender_email" character varying(50) NOT NULL,
    "recipient_user_id" integer NOT NULL,
    "assigned_robot" integer,
    "room_number" character varying(10) NOT NULL,
    "delivery_time" timestamp with time zone NOT NULL,
    "status" character varying(20) NOT NULL,
    "pin" character(6) DEFAULT "lpad"(("floor"(("random"() * (1000000)::double precision)))::"text", 6, '0'::"text") NOT NULL,
    CONSTRAINT "delivery_status_check" CHECK ((("status")::"text" = ANY ((ARRAY['no_robot'::character varying, 'ready'::character varying, 'in_progress'::character varying, 'error'::character varying, 'unloading'::character varying, 'complete'::character varying, 'late'::character varying])::"text"[])))
);


--
-- Name: delivery_delivery_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."delivery_delivery_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: delivery_delivery_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."delivery_delivery_id_seq" OWNED BY "public"."delivery"."delivery_id";


--
-- Name: message_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."message_log" (
    "message_id" integer NOT NULL,
    "sent_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "message_type" character varying(2) NOT NULL,
    "sender_robot_id" integer,
    "sender_user_id" integer,
    "recipient_robot_id" integer,
    "recipient_user_id" integer,
    "delivery_id" integer,
    "msg_text" character varying(500) NOT NULL,
    "msg_status" character varying(20) NOT NULL,
    CONSTRAINT "message_log_check" CHECK (((("sender_robot_id" IS NOT NULL) AND ("sender_user_id" IS NULL)) OR (("sender_robot_id" IS NULL) AND ("sender_user_id" IS NOT NULL)))),
    CONSTRAINT "message_log_check1" CHECK (((("recipient_robot_id" IS NOT NULL) AND ("recipient_user_id" IS NULL)) OR (("recipient_robot_id" IS NULL) AND ("recipient_user_id" IS NOT NULL)))),
    CONSTRAINT "message_log_message_type_check" CHECK ((("message_type")::"text" = ANY ((ARRAY['AR'::character varying, 'RA'::character varying, 'BA'::character varying, 'BR'::character varying])::"text"[]))),
    CONSTRAINT "message_log_msg_status_check" CHECK ((("msg_status")::"text" = ANY ((ARRAY['sent'::character varying, 'read'::character varying, 'unread'::character varying, 'error'::character varying])::"text"[])))
);


--
-- Name: message_log_message_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."message_log_message_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: message_log_message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."message_log_message_id_seq" OWNED BY "public"."message_log"."message_id";


--
-- Name: robot; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."robot" (
    "robot_id" integer NOT NULL,
    "robot_status" character varying(10) NOT NULL,
    "current_room" character varying(10),
    "next_room" character varying(10),
    CONSTRAINT "robot_robot_status_check" CHECK ((("robot_status")::"text" = ANY ((ARRAY['off'::character varying, 'idle'::character varying, 'charging'::character varying, 'moving'::character varying])::"text"[])))
);


--
-- Name: robot_event_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."robot_event_log" (
    "event_id" integer NOT NULL,
    "event_type" character varying(10) NOT NULL,
    "robot_id" integer NOT NULL,
    "delivery_id" integer,
    "event_time" timestamp with time zone DEFAULT "now"() NOT NULL,
    "description" character varying(200) NOT NULL,
    CONSTRAINT "robot_event_log_event_type_check" CHECK ((("event_type")::"text" = ANY ((ARRAY['operation'::character varying, 'warning'::character varying, 'error'::character varying, 'success'::character varying])::"text"[])))
);


--
-- Name: robot_event_log_event_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."robot_event_log_event_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: robot_event_log_event_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."robot_event_log_event_id_seq" OWNED BY "public"."robot_event_log"."event_id";


--
-- Name: robot_robot_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE "public"."robot_robot_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: robot_robot_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE "public"."robot_robot_id_seq" OWNED BY "public"."robot"."robot_id";


--
-- Name: room; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."room" (
    "room_number" character varying(10) NOT NULL,
    "floor_number" character varying(3) NOT NULL
);


--
-- Name: account user_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."account" ALTER COLUMN "user_id" SET DEFAULT "nextval"('"public"."account_user_id_seq"'::"regclass");


--
-- Name: delivery delivery_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."delivery" ALTER COLUMN "delivery_id" SET DEFAULT "nextval"('"public"."delivery_delivery_id_seq"'::"regclass");


--
-- Name: message_log message_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log" ALTER COLUMN "message_id" SET DEFAULT "nextval"('"public"."message_log_message_id_seq"'::"regclass");


--
-- Name: robot robot_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot" ALTER COLUMN "robot_id" SET DEFAULT "nextval"('"public"."robot_robot_id_seq"'::"regclass");


--
-- Name: robot_event_log event_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot_event_log" ALTER COLUMN "event_id" SET DEFAULT "nextval"('"public"."robot_event_log_event_id_seq"'::"regclass");


--
-- Data for Name: account; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."account" ("user_id", "username", "password_hash", "first_name", "last_name", "user_role", "email", "phone_number") FROM stdin;
3	test_user_1	fake_hash	Test	User	user	test@torontomu.ca	4165551234
1	dummy_admin	ronaldINHO80	John	Doe	admin	updated_dummy_email@notreal.ca	3434343434
6	test_user_123	$argon2id$v=19$m=65536,t=3,p=4$tbbWek+JUWoNASDEWOudkw$HW2ayKqhWW1ZBmUmGEs3nuq+sKdFtix1G8Z2vV7dTtM	Test	User	user	testuser@test.com	\N
8	jerry	$argon2id$v=19$m=65536,t=3,p=4$MQaAMGYModS69753jpGSMg$J5A+SnAS9OpzeUrNNcnvFWexmYIMs/yIAqdt65ON8ZE	jerry	jerry	user	jerry@jerry.com	1112223333
9	helloworld	$argon2id$v=19$m=65536,t=3,p=4$tTamdC5lTAlBCCHEmJNS6g$+o+ApCsQpyuG87Lo5/swFomegV49WnaYSertRMLfBbk	helloworld	helloworld	user	helloworld@helloworld.com	\N
2	dummy_user	$argon2id$v=19$m=65536,t=3,p=4$XevdW+t9b+09RwhhLMU4pw$73kJxnu+5x9oyB8yclXxFEw1gop3ff4ROp5HxBaozRg	Jane	Doe	user	jane_doe@notreal.ca	\N
5	admin	$argon2id$v=19$m=65536,t=3,p=4$Tuldq/Xe+//fW0tJyVkrBQ$m51QZjOB+wjsUpXsqLm3ghiPZ6/GJ8TrW63Sva1F36I	Test	Admin	admin	admin@tmu.com	4382238875
7	bob	$argon2id$v=19$m=65536,t=3,p=4$ay2FcO49x/ifc46xNoawdg$bvX1hPP03Iij6GGHWiVzibWEZe0bHtW+usILPgkQNPw	bob	bob	user	bob@b.com	3321234567
\.


--
-- Data for Name: delivery; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."delivery" ("delivery_id", "admin_user_id", "created_at", "last_updated_at", "sender_name", "sender_address", "sender_phone", "sender_email", "recipient_user_id", "assigned_robot", "room_number", "delivery_time", "status", "pin") FROM stdin;
1	5	2026-04-02 18:20:36.732597-04	2026-04-02 18:20:36.732597-04	Claudio Marchisio	Parma, Italy	\N	cmarchi@gmail.com	1	1	ENG601	2026-04-09 18:20:00-04	ready	725816
\.


--
-- Data for Name: message_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."message_log" ("message_id", "sent_at", "message_type", "sender_robot_id", "sender_user_id", "recipient_robot_id", "recipient_user_id", "delivery_id", "msg_text", "msg_status") FROM stdin;
\.


--
-- Data for Name: robot; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."robot" ("robot_id", "robot_status", "current_room", "next_room") FROM stdin;
1	idle	ENG602	\N
\.


--
-- Data for Name: robot_event_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."robot_event_log" ("event_id", "event_type", "robot_id", "delivery_id", "event_time", "description") FROM stdin;
\.


--
-- Data for Name: room; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."room" ("room_number", "floor_number") FROM stdin;
ENG601	6
ENG602	6
ENG603	6
ENG604	6
\.


--
-- Name: account_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."account_user_id_seq"', 9, true);


--
-- Name: delivery_delivery_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."delivery_delivery_id_seq"', 1, true);


--
-- Name: message_log_message_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."message_log_message_id_seq"', 1, false);


--
-- Name: robot_event_log_event_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."robot_event_log_event_id_seq"', 1, false);


--
-- Name: robot_robot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('"public"."robot_robot_id_seq"', 1, true);


--
-- Name: account account_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."account"
    ADD CONSTRAINT "account_email_key" UNIQUE ("email");


--
-- Name: account account_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."account"
    ADD CONSTRAINT "account_pkey" PRIMARY KEY ("user_id");


--
-- Name: account account_username_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."account"
    ADD CONSTRAINT "account_username_key" UNIQUE ("username");


--
-- Name: delivery delivery_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."delivery"
    ADD CONSTRAINT "delivery_pkey" PRIMARY KEY ("delivery_id");


--
-- Name: message_log message_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log"
    ADD CONSTRAINT "message_log_pkey" PRIMARY KEY ("message_id");


--
-- Name: robot_event_log robot_event_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot_event_log"
    ADD CONSTRAINT "robot_event_log_pkey" PRIMARY KEY ("event_id");


--
-- Name: robot robot_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot"
    ADD CONSTRAINT "robot_pkey" PRIMARY KEY ("robot_id");


--
-- Name: room room_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."room"
    ADD CONSTRAINT "room_pkey" PRIMARY KEY ("room_number");


--
-- Name: delivery delivery_admin_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."delivery"
    ADD CONSTRAINT "delivery_admin_user_id_fkey" FOREIGN KEY ("admin_user_id") REFERENCES "public"."account"("user_id");


--
-- Name: delivery delivery_assigned_robot_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."delivery"
    ADD CONSTRAINT "delivery_assigned_robot_fkey" FOREIGN KEY ("assigned_robot") REFERENCES "public"."robot"("robot_id");


--
-- Name: delivery delivery_recipient_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."delivery"
    ADD CONSTRAINT "delivery_recipient_user_id_fkey" FOREIGN KEY ("recipient_user_id") REFERENCES "public"."account"("user_id");


--
-- Name: delivery delivery_room_number_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."delivery"
    ADD CONSTRAINT "delivery_room_number_fkey" FOREIGN KEY ("room_number") REFERENCES "public"."room"("room_number");


--
-- Name: message_log message_log_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log"
    ADD CONSTRAINT "message_log_delivery_id_fkey" FOREIGN KEY ("delivery_id") REFERENCES "public"."delivery"("delivery_id");


--
-- Name: message_log message_log_recipient_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log"
    ADD CONSTRAINT "message_log_recipient_robot_id_fkey" FOREIGN KEY ("recipient_robot_id") REFERENCES "public"."robot"("robot_id");


--
-- Name: message_log message_log_recipient_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log"
    ADD CONSTRAINT "message_log_recipient_user_id_fkey" FOREIGN KEY ("recipient_user_id") REFERENCES "public"."account"("user_id");


--
-- Name: message_log message_log_sender_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log"
    ADD CONSTRAINT "message_log_sender_robot_id_fkey" FOREIGN KEY ("sender_robot_id") REFERENCES "public"."robot"("robot_id");


--
-- Name: message_log message_log_sender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."message_log"
    ADD CONSTRAINT "message_log_sender_user_id_fkey" FOREIGN KEY ("sender_user_id") REFERENCES "public"."account"("user_id");


--
-- Name: robot robot_current_room_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot"
    ADD CONSTRAINT "robot_current_room_fkey" FOREIGN KEY ("current_room") REFERENCES "public"."room"("room_number");


--
-- Name: robot_event_log robot_event_log_delivery_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot_event_log"
    ADD CONSTRAINT "robot_event_log_delivery_id_fkey" FOREIGN KEY ("delivery_id") REFERENCES "public"."delivery"("delivery_id");


--
-- Name: robot_event_log robot_event_log_robot_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot_event_log"
    ADD CONSTRAINT "robot_event_log_robot_id_fkey" FOREIGN KEY ("robot_id") REFERENCES "public"."robot"("robot_id");


--
-- Name: robot robot_next_room_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."robot"
    ADD CONSTRAINT "robot_next_room_fkey" FOREIGN KEY ("next_room") REFERENCES "public"."room"("room_number");


--
-- PostgreSQL database dump complete
--

\unrestrict cVsTTD1NKeInGMXticdYqUNWJa7uopSag9I8UylYsP7yRmpflMa6s6Bq6GMgTvw

