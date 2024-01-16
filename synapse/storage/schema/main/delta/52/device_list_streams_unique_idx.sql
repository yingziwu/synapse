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

-- register a background update which will create a unique index on
-- device_lists_remote_cache
INSERT into background_updates (update_name, progress_json)
    VALUES ('device_lists_remote_cache_unique_idx', '{}');

-- and one on device_lists_remote_extremeties
INSERT into background_updates (update_name, progress_json, depends_on)
    VALUES (
        'device_lists_remote_extremeties_unique_idx', '{}',

        -- doesn't really depend on this, but we need to make sure both happen
        -- before we drop the old indexes.
        'device_lists_remote_cache_unique_idx'
    );

-- once they complete, we can drop the old indexes.
INSERT into background_updates (update_name, progress_json, depends_on)
    VALUES (
        'drop_device_list_streams_non_unique_indexes', '{}',
        'device_lists_remote_extremeties_unique_idx'
    );
