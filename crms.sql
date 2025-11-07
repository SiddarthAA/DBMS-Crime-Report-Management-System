-- 1. Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'officer', 'citizen') NOT NULL,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    address TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Case Status (initially without crime_id FK)
CREATE TABLE case_status (
    status_id INT PRIMARY KEY AUTO_INCREMENT,
    status_name ENUM('Pending', 'Investigating', 'Resolved') NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crimes Table
CREATE TABLE crimes (
    crime_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    crime_type ENUM('Theft', 'Assault', 'Cybercrime', 'Homicide', 'Other') NOT NULL,
    location VARCHAR(255) NOT NULL,
    date_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status_id INT NOT NULL,
    officer_id INT NOT NULL,
    reported_by INT NOT NULL,
    FOREIGN KEY (status_id) REFERENCES case_status(status_id),
    FOREIGN KEY (officer_id) REFERENCES users(user_id),
    FOREIGN KEY (reported_by) REFERENCES users(user_id)
);

-- 4. Alter Case Status to add crime_id FK
ALTER TABLE case_status
ADD COLUMN crime_id INT NOT NULL,
ADD FOREIGN KEY (crime_id) REFERENCES crimes(crime_id) ON DELETE CASCADE;

-- 5. Criminals Table
CREATE TABLE criminals (
    criminal_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    alias VARCHAR(100),
    dob DATE NOT NULL,
    crime_history TEXT NOT NULL,
    last_arrest_date DATE NOT NULL
);

-- 6. Case Assignments Table
CREATE TABLE case_assignments (
    assignment_id INT PRIMARY KEY AUTO_INCREMENT,
    crime_id INT NOT NULL,
    officer_id INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crime_id) REFERENCES crimes(crime_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 7. Evidence Table
CREATE TABLE evidence (
    evidence_id INT PRIMARY KEY AUTO_INCREMENT,
    crime_id INT NOT NULL,
    evidence_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crime_id) REFERENCES crimes(crime_id) ON DELETE CASCADE
);

-- 8. Witnesses Table
CREATE TABLE witnesses (
    witness_id INT PRIMARY KEY AUTO_INCREMENT,
    crime_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    contact_info VARCHAR(100) NOT NULL,
    statement TEXT NOT NULL,
    FOREIGN KEY (crime_id) REFERENCES crimes(crime_id) ON DELETE CASCADE
);

-- 9. Reports Table
CREATE TABLE reports (
    report_id INT PRIMARY KEY AUTO_INCREMENT,
    crime_id INT NOT NULL,
    generated_by INT NOT NULL,
    report_content TEXT NOT NULL,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (crime_id) REFERENCES crimes(crime_id) ON DELETE CASCADE,
    FOREIGN KEY (generated_by) REFERENCES users(user_id) ON DELETE RESTRICT
);

-- 1. Insert into users
INSERT INTO users (name, email, password_hash, role, phone_number, address)
VALUES
('UserA', 'userA@example.com', 'password123', 'admin', '1234567890', '123 Main St, City, Country'),
('UserB', 'userB@example.com', 'password123', 'officer', '0987654321', '456 Elm St, City, Country'),
('UserC', 'userC@example.com', 'password123', 'citizen', '1122334455', '789 Oak St, City, Country');

-- 2. Insert into case_status
INSERT INTO case_status (status_name)
VALUES
('Pending'),
('Investigating'),
('Resolved');

-- 3. Insert into crimes (ensure status_id, officer_id, and reported_by exist in users table)
INSERT INTO crimes (title, description, crime_type, location, status_id, officer_id, reported_by)
VALUES
('Theft Incident', 'A theft occurred in the market area.', 'Theft', 'Market Street', 1, 2, 3),
('Assault on Citizen', 'A citizen was assaulted in the park.', 'Assault', 'City Park', 2, 2, 3),
('Cybercrime Alert', 'Suspicious online activity reported.', 'Cybercrime', 'Online', 3, 2, 3);

-- 4. Insert into criminals
INSERT INTO criminals (name, alias, dob, crime_history, last_arrest_date)
VALUES
('CriminalA', 'AliasA', '1990-01-01', 'Theft, Assault', '2023-05-10'),
('CriminalB', 'AliasB', '1985-05-15', 'Homicide, Fraud', '2023-03-22'),
('CriminalC', 'AliasC', '1992-08-25', 'Cybercrime, Theft', '2023-06-15');

-- 5. Insert into case_assignments
INSERT INTO case_assignments (crime_id, officer_id)
VALUES
(1, 2),
(2, 2),
(3, 2);

-- 6. Insert into evidence
INSERT INTO evidence (crime_id, evidence_type, description, file_path)
VALUES
(1, 'Fingerprint', 'Fingerprint found at the crime scene.', '/evidence/fingerprint1.jpg'),
(2, 'Weapon', 'Knife found at the scene.', '/evidence/weapon2.jpg'),
(3, 'Computer Logs', 'Suspicious activity logs from the suspect.', '/evidence/logs3.pdf');

-- 7. Insert into witnesses
INSERT INTO witnesses (crime_id, name, contact_info, statement)
VALUES
(1, 'WitnessA', 'witnessA@example.com', 'Saw the suspect fleeing the scene.'),
(2, 'WitnessB', 'witnessB@example.com', 'Heard a loud argument and then an assault.'),
(3, 'WitnessC', 'witnessC@example.com', 'Saw the suspect engage in illegal online activity.');

-- 8. Insert into reports
INSERT INTO reports (crime_id, generated_by, report_content)
VALUES
(1, 1, 'Theft incident report for Market Street. Details as per witness A.'),
(2, 1, 'Assault report for City Park. Based on witness statements.'),
(3, 1, 'Cybercrime report. Logs and witness statements collected.');

ALTER TABLE case_assignments
ADD UNIQUE KEY unique_assignment (crime_id, officer_id);
