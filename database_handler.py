import psycopg2
from psycopg2.extras import DictCursor

class DatabaseConnection:
    _instance = None
    _connection = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._connection:
            try:
                self._connection = psycopg2.connect(
                    host="localhost",
                    port="5432",
                    dbname="postgres",
                    user="postgres",
                    password="admin123"
                )
            except Exception as e:
                print(f"Failed to connect to database: {e}")

    def get_connection(self):
        return self._connection

    def disconnect(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None


# class FOLSentence:
#     def __init__(self, sentence_id, data, predicates: list, constants: list, difficulty):
#         self.sentence_id = sentence_id
#         self.data = data
#         self.predicates = predicates
#         self.constants = constants
#         self.difficulty = difficulty
#
#     def getId(self):
#         return self.sentence_id
#
#     def getData(self):
#         return self.data
#
#     def getPredicates(self):
#         return self.predicates
#
#     def getConstants(self):
#         return self.constants
#
#     def getDifficulty(self):
#         return self.difficulty
#
#     def __str__(self):
#         return f"id: {self.sentence_id}" + "; fol_sentence: " + self.data + "; predicates: " + self.predicates.__str__() + "; constants: " + self.constants.__str__() + "; diff: " + self.difficulty
#
#     def __eq__(self, other):
#         return self.sentence_id == other.sentence_id


def createDatabase():
    db = DatabaseConnection()
    conn = db.get_connection()

    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS sentence_constant CASCADE;
        DROP TABLE IF EXISTS constant CASCADE;
        DROP TABLE IF EXISTS sentence_predicate CASCADE;
        DROP TABLE IF EXISTS predicate CASCADE;
        DROP TABLE IF EXISTS sentence CASCADE;

        CREATE TABLE IF NOT EXISTS sentence (
            id SERIAL PRIMARY KEY,
            english_sentence TEXT NOT NULL,
            fol_sentence TEXT NOT NULL,
            difficulty VARCHAR(255)
        );

        CREATE TABLE IF NOT EXISTS predicate (
            id SERIAL PRIMARY KEY,
            data VARCHAR(255) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sentence_predicate (
            sentence_id INT REFERENCES sentence (id) ON DELETE CASCADE,
            predicate_id INT REFERENCES predicate (id) ON DELETE CASCADE,
            CONSTRAINT sentence_predicate_pkey PRIMARY KEY (sentence_id, predicate_id)
        );

        CREATE TABLE IF NOT EXISTS constant (
            id SERIAL PRIMARY KEY,
            data VARCHAR(255) NOT NULL
        );

        CREATE TABLE IF NOT EXISTS sentence_constant (
            sentence_id INT REFERENCES sentence (id) ON DELETE CASCADE,
            constant_id INT REFERENCES constant (id) ON DELETE CASCADE,
            CONSTRAINT sentence_constant_pkey PRIMARY KEY (sentence_id, constant_id)
        );
    """)

    cur.execute("""
        INSERT INTO sentence(english_sentence, fol_sentence, difficulty)
        VALUES ('All humans are mortal.', 'all x. (human(x) -> mortal(x))', 'low'), --1
            ('Socrates is a human.', 'human(socrates)', 'low'), --2
            ('If it rains, the ground is wet.', 'all x. (rains(x) -> wet(ground))', 'low'), --3
             ('The sun is bright.', 'bright(sun)', 'low'), --4
             ('All cats are animals.', 'all x. (cat(x) -> animal(x))', 'low'), --5
             ('Some animals have tails.', 'exists x. (animal(x) & has_tail(x))', 'low'), --6
             ('John likes apples.', 'likes(john, apple)', 'medium'), --7
             ('Birds can fly.', 'all x. (bird(x) -> can_fly(x))', 'low'), --8
             ('There exists a person who is happy.', 'exists x. (person(x) & happy(x))', 'medium'), --9
             ('Water is necessary for life.', 'necessary(water, life)', 'low'), --10
             ('If someone studies hard, they pass the exam.', 'all x. (studies_hard(x) -> passes_exam(x))', 'medium'), --11
             ('No fish can fly.', 'all x. (fish(x) -> -can_fly(x))', 'medium'), --12
             ('Some students are tired.', 'exists x. (student(x) & tired(x))', 'medium'); --13
    """)

    cur.execute("""
        INSERT INTO predicate(data)
        VALUES ('human(x)'), --1
            ('mortal(x)'), --2
            ('rains(x)'), --3
            ('wet(x)'), --4
            ('bright(x)'), --5
            ('cat(x)'), --6
            ('animal(x)'), --7
            ('has_tail(x)'), --8
            ('likes(x, y)'), --9
            ('bird(x)'), --10
            ('can_fly(x)'), --11
            ('person(x)'), --12
            ('happy(x)'), --13
            ('necessary(x, y)'), --14
            ('studies_hard(x)'), --15
            ('passes_exam(x)'), --16
            ('fish(x)'), --17
            ('student(x)'), --18
            ('tired(x)'); --19
    """)

    cur.execute("""
        INSERT INTO constant(data)
        VALUES ('socrates'), --1
            ('ground'), --2
            ('sun'), --3 
            ('john'), --4
            ('apple'), --5
            ('water'), --6 
            ('life'); --7
    """)

    cur.execute("""
        INSERT INTO sentence_predicate(sentence_id, predicate_id)
        VALUES (1, 1),
            (1, 2),
            (2, 1),
            (3, 3),
            (3, 4),
            (4, 5),
            (5, 6),
            (5, 7),
            (6, 7),
            (6, 8),
            (7, 9),
            (8, 10),
            (8, 11),
            (9, 12),
            (9, 13),
            (10, 14),
            (11, 15),
            (11, 16),
            (12, 17),
            (12, 11),
            (13, 18),
            (13, 19);
    """)

    cur.execute("""
           INSERT INTO sentence_constant(sentence_id, constant_id)
           VALUES (2, 1),
               (3, 2),
               (4, 3),
               (7, 4),
               (7, 5),
               (10, 6),
               (10, 7);
       """)

    conn.commit()

    cur.close()
    conn.close()
    db.disconnect()


def getFOLSentences():
    db = DatabaseConnection()
    conn = db.get_connection()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT 
            fol.id as id,
            fol.fol_sentence as fol_sentence,
            array_agg(DISTINCT p.data) as predicates,
            array_agg(DISTINCT c.data) as constants,
            fol.difficulty as difficulty
        FROM sentence fol
        LEFT JOIN public.sentence_constant sc on fol.id = sc.sentence_id
        LEFT JOIN public.sentence_predicate sp on fol.id = sp.sentence_id
        LEFT JOIN public.constant c on c.id = sc.constant_id
        LEFT JOIN public.predicate p on p.id = sp.predicate_id
        GROUP BY fol.id
        ORDER BY id
    """)
    sentences = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()
    db.disconnect()
    return sentences


def getFOLSentenceById(sentence_id: int):
    db = DatabaseConnection()
    conn = db.get_connection()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
            SELECT 
                fol.id as id,
                fol.fol_sentence as fol_sentence,
                array_agg(DISTINCT p.data) as predicates,
                array_agg(DISTINCT c.data) as constants,
                fol.difficulty as difficulty
            FROM sentence fol
            LEFT JOIN public.sentence_constant sc on fol.id = sc.sentence_id
            LEFT JOIN public.sentence_predicate sp on fol.id = sp.sentence_id
            LEFT JOIN public.constant c on c.id = sc.constant_id
            LEFT JOIN public.predicate p on p.id = sp.predicate_id
            WHERE fol.id = %s
            GROUP BY fol.id
        """, (sentence_id,))
    row = cur.fetchone()
    sentence = dict(row) if row else None

    cur.close()
    conn.close()
    db.disconnect()
    return sentence

def getRandomSentences():
    db = DatabaseConnection()
    conn = db.get_connection()
    cur = conn.cursor(cursor_factory=DictCursor)

    cur.execute("""
        SELECT 
            fol.id AS id,
            fol.english_sentence AS english_sentence,
            fol.fol_sentence AS fol_sentence,
            array_agg(DISTINCT p.data) AS predicates,
            array_agg(DISTINCT c.data) AS constants,
            fol.difficulty AS difficulty
        FROM sentence fol
        LEFT JOIN public.sentence_predicate sp ON fol.id = sp.sentence_id
        LEFT JOIN public.predicate p ON p.id = sp.predicate_id
        LEFT JOIN public.sentence_constant sc ON fol.id = sc.sentence_id
        LEFT JOIN public.constant c ON c.id = sc.constant_id
        GROUP BY fol.id
        ORDER BY RANDOM()
        LIMIT 10;
    """)

    sentences = [dict(row) for row in cur.fetchall()]

    cur.close()
    conn.close()
    db.disconnect()
    return sentences