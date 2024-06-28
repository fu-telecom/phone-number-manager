
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

CREATE TABLE IF NOT EXISTS service_signups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fut_event_id INT,
    FOREIGN KEY (fut_event_id) REFERENCES fut_events(id),
    camp_name VARCHAR(255) NOT NULL,
    camp_lead_name VARCHAR(255) NOT NULL,
    camp_lead_phone VARCHAR(255) NOT NULL,
    camp_lead_email VARCHAR(255) NOT NULL,
    submitter_name VARCHAR(255) NOT NULL,
    submitter_phone VARCHAR(255) NOT NULL,
    submitter_email VARCHAR(255) NOT NULL,
    desired_number VARCHAR(255) NOT NULL,
    desired_callerid VARCHAR(255) NOT NULL,
    own_phone TINYINT(1) NOT NULL DEFAULT 0,
    message TEXT NULL,
    submitted_at TIMESTAMP
);
