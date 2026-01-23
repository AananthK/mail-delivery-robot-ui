-- Development seed data
-- DO NOT use in production

-- Creating a test 'dummy' admin
INSERT INTO account (username, password_hash, first_name, last_name, user_role, email)
VALUES ('dummy_admin', 'dummy_pword_hash', 'John', 'Doe','admin', 'dummy_admin@notreal.ca');

-- Creating a test 'dummy' user
INSERT INTO account (username, password_hash, first_name, last_name, user_role, email)
VALUES ('dummy_user', 'dummy_pword_hash', 'Jane', 'Doe','user', 'dummy_user@notreal.ca');

-- Creating a test room
INSERT INTO room (room_number, floor_number)
VALUES ('ENG601', '6');

-- Verifying accounts were created
SELECT * FROM account;

-- Verifying room was created
SELECT * FROM room;