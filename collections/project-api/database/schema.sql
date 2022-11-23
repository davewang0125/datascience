CREATE DATABASE meetings;
USE meetings;

CREATE TABLE users (
id int,
username varchar(255) NOT NULL,
email varchar(255) NOT NULL,
PRIMARY KEY (id)
);

CREATE TABLE meetings (
id int,
startTime datetime NOT NULL,
endTime datetime NOT NULL,
location varchar(255) DEFAULT "Virginia",
location_id int DEFAULT 1,
host_id int,
PRIMARY KEY (id),
FOREIGN KEY (host_id) REFERENCES users(id)
-- FOREIGN KEY (location_id) REFERENCES servers(location_id)
);

CREATE TABLE participants (
    participant_id int,
    meeting_id int,
    start_time datetime NOT NULL,
    end_time datetime NOT NULL,
    is_host bool,
    FOREIGN KEY (participant_id) REFERENCES users(id),
    FOREIGN KEY (meeting_id) REFERENCES meetings(id),
    CHECK (start_time < end_time)
);

CREATE TABLE transcripts (
meeting_id int,
speaker_id int,
start_time datetime,
end_time datetime,
content text,
audio mediumtext,
content_lang varchar(255) DEFAULT "english",
FOREIGN KEY (speaker_id) REFERENCES users(id),
FOREIGN KEY (meeting_id) REFERENCES meetings(id),
CHECK (start_time < end_time)
);


