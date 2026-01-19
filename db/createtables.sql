CREATE TABLE account (
user_id SERIAL PRIMARY KEY,
username VARCHAR(30) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
first_name VARCHAR(20) NOT NULL,
last_name VARCHAR(20) NOT NULL,
user_role VARCHAR(5) NOT NULL CHECK (user_role IN('admin','user')),
email VARCHAR(50) NOT NULL UNIQUE,
phone_number VARCHAR(11)
);

CREATE TABLE room (
room_number VARCHAR(10) PRIMARY KEY,
floor_number VARCHAR(3) NOT NULL 
);

CREATE TABLE robot (
robot_id SERIAL PRIMARY KEY,
robot_status VARCHAR(10) NOT NULL CHECK (robot_status IN('off','idle', 'charging', 'moving')),
current_room VARCHAR(10) REFERENCES room (room_number),
next_room VARCHAR(10) REFERENCES room (room_number)
);

CREATE TABLE delivery (
delivery_id SERIAL PRIMARY KEY,
admin_user_id INTEGER NOT NULL REFERENCES account (user_id),
created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
last_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
sender_name VARCHAR (30) NOT NULL,
sender_address VARCHAR (50) NOT NULL,
sender_phone VARCHAR (11),
sender_email VARCHAR (50) NOT NULL,
recipient_user_id INTEGER NOT NULL REFERENCES account (user_id),
assigned_robot INTEGER REFERENCES robot (robot_id),
room_number VARCHAR(10) NOT NULL REFERENCES room (room_number),
delivery_time TIMESTAMPTZ NOT NULL,
status VARCHAR (20) NOT NULL CHECK (status IN ('no_robot','ready','in_progress','error','unloading','complete'))
);

CREATE TABLE robot_event_log (
event_id SERIAL PRIMARY KEY,
event_type VARCHAR(10) NOT NULL CHECK (event_type IN ('operation','warning','error','success')),
robot_id INTEGER NOT NULL REFERENCES robot (robot_id),
delivery_id INTEGER REFERENCES delivery (delivery_id),
event_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
description VARCHAR(200) NOT NULL
);

CREATE TABLE message_log (
message_id SERIAL PRIMARY KEY,
sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
message_type VARCHAR(2) NOT NULL CHECK(message_type IN ('AR','RA','BA','BR')),
sender_robot_id INTEGER REFERENCES robot (robot_id),
sender_user_id INTEGER REFERENCES account (user_id),
recipient_robot_id INTEGER REFERENCES robot (robot_id),
recipient_user_id INTEGER REFERENCES account (user_id),
delivery_id INTEGER REFERENCES delivery (delivery_id),
msg_text VARCHAR (500) NOT NULL,
msg_status VARCHAR (20) NOT NULL CHECK (msg_status IN ('sent','read','unread','error')),

-- To ensure exactly one sender and one receiver irrespective of endpoint types
  CHECK (
    (sender_robot_id IS NOT NULL AND sender_user_id IS NULL)
    OR
    (sender_robot_id IS NULL AND sender_user_id IS NOT NULL)
  ),

  CHECK (
    (recipient_robot_id IS NOT NULL AND recipient_user_id IS NULL)
    OR
    (recipient_robot_id IS NULL AND recipient_user_id IS NOT NULL)
  )
);