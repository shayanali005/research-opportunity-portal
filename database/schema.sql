CREATE DATABASE IF NOT EXISTS research_atlas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE research_atlas;
CREATE TABLE IF NOT EXISTS opportunities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    research_title VARCHAR(200) NOT NULL,
    research_description TEXT NOT NULL,
    research_area VARCHAR(100) NOT NULL,
    faculty_name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    required_skills VARCHAR(255) NOT NULL,
    available_positions INT NOT NULL,
    application_deadline DATE NOT NULL,
    status ENUM('Open','Closed') NOT NULL DEFAULT 'Open',
    CONSTRAINT positive_positions CHECK (available_positions > 0),
    INDEX deadline_index (application_deadline),
    INDEX status_index (status)
);
