
CREATE TABLE IF NOT EXISTS fut_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    CONSTRAINT title_not_blank CHECK (title <> ''),
    CONSTRAINT end_after_start CHECK (end_date >= start_date)
);

-- INSERT INTO fut_events (title, start_date, end_date) VALUES ('Flipside 2024', '2024-05-23', '2024-05-29');
