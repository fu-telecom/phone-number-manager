
CREATE TABLE IF NOT EXISTS fut_events (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL UNIQUE,
    event_start_date DATE NOT NULL,
    event_end_date DATE NOT NULL,
    reg_start_date DATE NOT NULL,
    reg_end_date DATE NOT NULL,
    CONSTRAINT title_not_blank CHECK (title <> ''),
    CONSTRAINT event_end_after_start CHECK (event_end_date >= event_start_date),
    CONSTRAINT reg_end_after_start CHECK (reg_end_date >= reg_start_date)
);

-- INSERT INTO fut_events (title, event_start_date, event_end_date, reg_start_date, reg_end_date) VALUES ('Flipside 2025', '2025-05-22', '2025-05-26', '2024-06-01', '2025-05-16');
