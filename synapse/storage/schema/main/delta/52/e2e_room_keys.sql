--
-- This file is licensed under the Affero General Public License (AGPL) version 3.
--
-- Copyright (C) 2023 New Vector, Ltd
--
-- This program is free software: you can redistribute it and/or modify
-- it under the terms of the GNU Affero General Public License as
-- published by the Free Software Foundation, either version 3 of the
-- License, or (at your option) any later version.
--
-- See the GNU Affero General Public License for more details:
-- <https://www.gnu.org/licenses/agpl-3.0.html>.
--
-- Originally licensed under the Apache License, Version 2.0:
-- <http://www.apache.org/licenses/LICENSE-2.0>.
--
-- [This file includes modifications made by New Vector Limited]
--
--
/* Copyright 2018 New Vector Ltd
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/* Change version column to an integer so we can do MAX() sensibly
 */
CREATE TABLE e2e_room_keys_versions_new (
    user_id TEXT NOT NULL,
    version BIGINT NOT NULL,
    algorithm TEXT NOT NULL,
    auth_data TEXT NOT NULL,
    deleted SMALLINT DEFAULT 0 NOT NULL
);

INSERT INTO e2e_room_keys_versions_new
    SELECT user_id, CAST(version as BIGINT), algorithm, auth_data, deleted FROM e2e_room_keys_versions;

DROP TABLE e2e_room_keys_versions;
ALTER TABLE e2e_room_keys_versions_new RENAME TO e2e_room_keys_versions;

CREATE UNIQUE INDEX e2e_room_keys_versions_idx ON e2e_room_keys_versions(user_id, version);

/* Change e2e_rooms_keys to match
 */
CREATE TABLE e2e_room_keys_new (
    user_id TEXT NOT NULL,
    room_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    version BIGINT NOT NULL,
    first_message_index INT,
    forwarded_count INT,
    is_verified BOOLEAN,
    session_data TEXT NOT NULL
);

INSERT INTO e2e_room_keys_new
    SELECT user_id, room_id, session_id, CAST(version as BIGINT), first_message_index, forwarded_count, is_verified, session_data FROM e2e_room_keys;

DROP TABLE e2e_room_keys;
ALTER TABLE e2e_room_keys_new RENAME TO e2e_room_keys;

CREATE UNIQUE INDEX e2e_room_keys_idx ON e2e_room_keys(user_id, room_id, session_id);
