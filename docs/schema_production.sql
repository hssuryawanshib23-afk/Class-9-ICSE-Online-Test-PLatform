--
-- PostgreSQL database dump
--

\restrict 3XOnPuTWDzy2xw4h2iwZJ7CvCjyb1iiyQaaRP0U2H3BmaOcQXS2tfAWuAmcwbot

-- Dumped from database version 16.15 (df8277c)
-- Dumped by pg_dump version 18.6 (Debian 18.6-1.pgdg13+2)

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

--
-- Name: alerting; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA alerting;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_test_attempts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_test_attempts (
    attempt_id integer NOT NULL,
    admin_test_id integer,
    user_id integer,
    score integer NOT NULL,
    total_questions integer NOT NULL,
    percentage numeric(5,2) NOT NULL,
    attempted_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: admin_test_attempts_attempt_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admin_test_attempts_attempt_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_test_attempts_attempt_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admin_test_attempts_attempt_id_seq OWNED BY public.admin_test_attempts.attempt_id;


--
-- Name: admin_test_questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_test_questions (
    id integer NOT NULL,
    admin_test_id integer,
    question_id integer,
    question_order integer NOT NULL
);


--
-- Name: admin_test_questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admin_test_questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_test_questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admin_test_questions_id_seq OWNED BY public.admin_test_questions.id;


--
-- Name: admin_test_responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_test_responses (
    response_id integer NOT NULL,
    attempt_id integer,
    question_id integer,
    selected_answer character(1),
    is_correct integer DEFAULT 0
);


--
-- Name: admin_test_responses_response_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admin_test_responses_response_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_test_responses_response_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admin_test_responses_response_id_seq OWNED BY public.admin_test_responses.response_id;


--
-- Name: admin_tests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.admin_tests (
    admin_test_id integer NOT NULL,
    test_name character varying(255) NOT NULL,
    created_by integer,
    total_questions integer NOT NULL,
    duration_minutes integer NOT NULL,
    easy_percentage integer DEFAULT 30,
    medium_percentage integer DEFAULT 30,
    hard_percentage integer DEFAULT 40,
    chapters text NOT NULL,
    is_active boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    allow_retake boolean DEFAULT false
);

ALTER TABLE ONLY public.admin_tests REPLICA IDENTITY FULL;


--
-- Name: admin_tests_admin_test_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.admin_tests_admin_test_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: admin_tests_admin_test_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.admin_tests_admin_test_id_seq OWNED BY public.admin_tests.admin_test_id;


--
-- Name: chapters; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.chapters (
    id integer NOT NULL,
    chapter_number integer NOT NULL,
    subject character varying(50) DEFAULT 'Physics'::character varying,
    chapter_name character varying(255)
);

ALTER TABLE ONLY public.chapters REPLICA IDENTITY FULL;


--
-- Name: chapters_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.chapters_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: chapters_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.chapters_id_seq OWNED BY public.chapters.id;


--
-- Name: concepts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.concepts (
    id integer NOT NULL,
    chapter_id integer,
    concept_name text NOT NULL,
    concept_type character varying(50)
);

ALTER TABLE ONLY public.concepts REPLICA IDENTITY FULL;


--
-- Name: concepts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.concepts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: concepts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.concepts_id_seq OWNED BY public.concepts.id;


--
-- Name: mcq_options; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.mcq_options (
    id integer NOT NULL,
    question_id integer,
    label character(1) NOT NULL,
    option_text text NOT NULL,
    is_correct integer DEFAULT 0
);


--
-- Name: mcq_options_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.mcq_options_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: mcq_options_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.mcq_options_id_seq OWNED BY public.mcq_options.id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.questions (
    id integer NOT NULL,
    concept_id integer,
    difficulty character varying(20) NOT NULL,
    question_text text NOT NULL,
    form character varying(50),
    thinking_type character varying(50),
    correct_label character varying(10),
    key_concept text
);

ALTER TABLE ONLY public.questions REPLICA IDENTITY FULL;


--
-- Name: questions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.questions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: questions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.questions_id_seq OWNED BY public.questions.id;


--
-- Name: responses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.responses (
    id integer NOT NULL,
    attempt_id integer,
    question_id integer,
    selected_label character(1),
    is_correct integer DEFAULT 0
);


--
-- Name: responses_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.responses_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: responses_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.responses_id_seq OWNED BY public.responses.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.students (
    user_id integer NOT NULL,
    name character varying(255),
    class character varying(10)
);


--
-- Name: test_attempts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.test_attempts (
    id integer NOT NULL,
    student_id integer,
    total_questions integer NOT NULL,
    score integer NOT NULL,
    started_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: test_attempts_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.test_attempts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: test_attempts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.test_attempts_id_seq OWNED BY public.test_attempts.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    password_hash text NOT NULL,
    role character varying(50) DEFAULT 'student'::character varying,
    phone_number character varying(15) NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    school_name character varying(255),
    class_name character varying(50),
    board_name character varying(100),
    recovery_code character varying(8)
);

ALTER TABLE ONLY public.users REPLICA IDENTITY FULL;


--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: admin_test_attempts attempt_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_attempts ALTER COLUMN attempt_id SET DEFAULT nextval('public.admin_test_attempts_attempt_id_seq'::regclass);


--
-- Name: admin_test_questions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_questions ALTER COLUMN id SET DEFAULT nextval('public.admin_test_questions_id_seq'::regclass);


--
-- Name: admin_test_responses response_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_responses ALTER COLUMN response_id SET DEFAULT nextval('public.admin_test_responses_response_id_seq'::regclass);


--
-- Name: admin_tests admin_test_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_tests ALTER COLUMN admin_test_id SET DEFAULT nextval('public.admin_tests_admin_test_id_seq'::regclass);


--
-- Name: chapters id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chapters ALTER COLUMN id SET DEFAULT nextval('public.chapters_id_seq'::regclass);


--
-- Name: concepts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.concepts ALTER COLUMN id SET DEFAULT nextval('public.concepts_id_seq'::regclass);


--
-- Name: mcq_options id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mcq_options ALTER COLUMN id SET DEFAULT nextval('public.mcq_options_id_seq'::regclass);


--
-- Name: questions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions ALTER COLUMN id SET DEFAULT nextval('public.questions_id_seq'::regclass);


--
-- Name: responses id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.responses ALTER COLUMN id SET DEFAULT nextval('public.responses_id_seq'::regclass);


--
-- Name: test_attempts id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_attempts ALTER COLUMN id SET DEFAULT nextval('public.test_attempts_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: admin_test_attempts admin_test_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_attempts
    ADD CONSTRAINT admin_test_attempts_pkey PRIMARY KEY (attempt_id);


--
-- Name: admin_test_questions admin_test_questions_admin_test_id_question_id_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_questions
    ADD CONSTRAINT admin_test_questions_admin_test_id_question_id_key UNIQUE (admin_test_id, question_id);


--
-- Name: admin_test_questions admin_test_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_questions
    ADD CONSTRAINT admin_test_questions_pkey PRIMARY KEY (id);


--
-- Name: admin_test_responses admin_test_responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_responses
    ADD CONSTRAINT admin_test_responses_pkey PRIMARY KEY (response_id);


--
-- Name: admin_tests admin_tests_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_tests
    ADD CONSTRAINT admin_tests_pkey PRIMARY KEY (admin_test_id);


--
-- Name: chapters chapters_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.chapters
    ADD CONSTRAINT chapters_pkey PRIMARY KEY (id);


--
-- Name: concepts concepts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.concepts
    ADD CONSTRAINT concepts_pkey PRIMARY KEY (id);


--
-- Name: mcq_options mcq_options_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mcq_options
    ADD CONSTRAINT mcq_options_pkey PRIMARY KEY (id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (id);


--
-- Name: responses responses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (user_id);


--
-- Name: test_attempts test_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_attempts
    ADD CONSTRAINT test_attempts_pkey PRIMARY KEY (id);


--
-- Name: users users_phone_number_unique; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_phone_number_unique UNIQUE (phone_number);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_admin_test_attempts_test; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_admin_test_attempts_test ON public.admin_test_attempts USING btree (admin_test_id);


--
-- Name: idx_admin_test_attempts_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_admin_test_attempts_user ON public.admin_test_attempts USING btree (user_id);


--
-- Name: idx_admin_test_questions_test; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_admin_test_questions_test ON public.admin_test_questions USING btree (admin_test_id);


--
-- Name: idx_admin_test_responses_attempt; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_admin_test_responses_attempt ON public.admin_test_responses USING btree (attempt_id);


--
-- Name: idx_admin_tests_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_admin_tests_active ON public.admin_tests USING btree (is_active);


--
-- Name: idx_admin_tests_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_admin_tests_created_by ON public.admin_tests USING btree (created_by);


--
-- Name: idx_concepts_chapter; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_concepts_chapter ON public.concepts USING btree (chapter_id);


--
-- Name: idx_mcq_options_question; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_mcq_options_question ON public.mcq_options USING btree (question_id);


--
-- Name: idx_questions_concept; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_questions_concept ON public.questions USING btree (concept_id);


--
-- Name: idx_responses_attempt; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_responses_attempt ON public.responses USING btree (attempt_id);


--
-- Name: idx_responses_question; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_responses_question ON public.responses USING btree (question_id);


--
-- Name: idx_test_attempts_student; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_test_attempts_student ON public.test_attempts USING btree (student_id);


--
-- Name: admin_test_attempts admin_test_attempts_admin_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_attempts
    ADD CONSTRAINT admin_test_attempts_admin_test_id_fkey FOREIGN KEY (admin_test_id) REFERENCES public.admin_tests(admin_test_id) ON DELETE CASCADE;


--
-- Name: admin_test_attempts admin_test_attempts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_attempts
    ADD CONSTRAINT admin_test_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: admin_test_questions admin_test_questions_admin_test_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_questions
    ADD CONSTRAINT admin_test_questions_admin_test_id_fkey FOREIGN KEY (admin_test_id) REFERENCES public.admin_tests(admin_test_id) ON DELETE CASCADE;


--
-- Name: admin_test_questions admin_test_questions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_questions
    ADD CONSTRAINT admin_test_questions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;


--
-- Name: admin_test_responses admin_test_responses_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_responses
    ADD CONSTRAINT admin_test_responses_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.admin_test_attempts(attempt_id) ON DELETE CASCADE;


--
-- Name: admin_test_responses admin_test_responses_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_test_responses
    ADD CONSTRAINT admin_test_responses_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;


--
-- Name: admin_tests admin_tests_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.admin_tests
    ADD CONSTRAINT admin_tests_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: concepts concepts_chapter_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.concepts
    ADD CONSTRAINT concepts_chapter_id_fkey FOREIGN KEY (chapter_id) REFERENCES public.chapters(id) ON DELETE CASCADE;


--
-- Name: mcq_options mcq_options_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.mcq_options
    ADD CONSTRAINT mcq_options_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;


--
-- Name: questions questions_concept_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_concept_id_fkey FOREIGN KEY (concept_id) REFERENCES public.concepts(id) ON DELETE CASCADE;


--
-- Name: responses responses_attempt_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_attempt_id_fkey FOREIGN KEY (attempt_id) REFERENCES public.test_attempts(id) ON DELETE CASCADE;


--
-- Name: responses responses_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.responses
    ADD CONSTRAINT responses_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id) ON DELETE CASCADE;


--
-- Name: students students_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: test_attempts test_attempts_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.test_attempts
    ADD CONSTRAINT test_attempts_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 3XOnPuTWDzy2xw4h2iwZJ7CvCjyb1iiyQaaRP0U2H3BmaOcQXS2tfAWuAmcwbot

