#
# This file is licensed under the Affero General Public License (AGPL) version 3.
#
# Copyright 2014-2016 OpenMarket Ltd
# Copyright (C) 2023 New Vector, Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# See the GNU Affero General Public License for more details:
# <https://www.gnu.org/licenses/agpl-3.0.html>.
#
# Originally licensed under the Apache License, Version 2.0:
# <http://www.apache.org/licenses/LICENSE-2.0>.
#
# [This file includes modifications made by New Vector Limited]
#
#

import logging
from typing import Optional

from synapse.storage._base import SQLBaseStore

logger = logging.getLogger(__name__)


class RejectionsStore(SQLBaseStore):
    async def get_rejection_reason(self, event_id: str) -> Optional[str]:
        return await self.db_pool.simple_select_one_onecol(
            table="rejections",
            retcol="reason",
            keyvalues={"event_id": event_id},
            allow_none=True,
            desc="get_rejection_reason",
        )
