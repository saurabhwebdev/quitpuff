CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    name TEXT,
    age INTEGER,
    cigs_per_day INTEGER,
    cost_per_cig FLOAT,
    currency TEXT,
    cigs_per_pack INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cigarettes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    smoked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cost FLOAT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
); 