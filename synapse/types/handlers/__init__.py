#
# This file is licensed under the Affero General Public License (AGPL) version 3.
#
# Copyright (C) 2024 New Vector, Ltd
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
from enum import Enum
from typing import TYPE_CHECKING, Dict, Final, List, Optional, Tuple

import attr
from typing_extensions import TypedDict

from synapse._pydantic_compat import HAS_PYDANTIC_V2

if TYPE_CHECKING or HAS_PYDANTIC_V2:
    from pydantic.v1 import Extra
else:
    from pydantic import Extra

from synapse.events import EventBase
from synapse.types import JsonMapping, StreamToken, UserID
from synapse.types.rest.client import SlidingSyncBody


class ShutdownRoomParams(TypedDict):
    """
    Attributes:
        requester_user_id:
            User who requested the action. Will be recorded as putting the room on the
            blocking list.
        new_room_user_id:
            If set, a new room will be created with this user ID
            as the creator and admin, and all users in the old room will be
            moved into that room. If not set, no new room will be created
            and the users will just be removed from the old room.
        new_room_name:
            A string representing the name of the room that new users will
            be invited to. Defaults to `Content Violation Notification`
        message:
            A string containing the first message that will be sent as
            `new_room_user_id` in the new room. Ideally this will clearly
            convey why the original room was shut down.
            Defaults to `Sharing illegal content on this server is not
            permitted and rooms in violation will be blocked.`
        block:
            If set to `true`, this room will be added to a blocking list,
            preventing future attempts to join the room. Defaults to `false`.
        purge:
            If set to `true`, purge the given room from the database.
        force_purge:
            If set to `true`, the room will be purged from database
            even if there are still users joined to the room.
    """

    requester_user_id: Optional[str]
    new_room_user_id: Optional[str]
    new_room_name: Optional[str]
    message: Optional[str]
    block: bool
    purge: bool
    force_purge: bool


class ShutdownRoomResponse(TypedDict):
    """
    Attributes:
        kicked_users: An array of users (`user_id`) that were kicked.
        failed_to_kick_users:
            An array of users (`user_id`) that that were not kicked.
        local_aliases:
            An array of strings representing the local aliases that were
            migrated from the old room to the new.
        new_room_id: A string representing the room ID of the new room.
    """

    kicked_users: List[str]
    failed_to_kick_users: List[str]
    local_aliases: List[str]
    new_room_id: Optional[str]


class SlidingSyncConfig(SlidingSyncBody):
    """
    Inherit from `SlidingSyncBody` since we need all of the same fields and add a few
    extra fields that we need in the handler
    """

    user: UserID
    device_id: Optional[str]

    # Pydantic config
    class Config:
        # By default, ignore fields that we don't recognise.
        extra = Extra.ignore
        # By default, don't allow fields to be reassigned after parsing.
        allow_mutation = False
        # Allow custom types like `UserID` to be used in the model
        arbitrary_types_allowed = True


class OperationType(Enum):
    """
    Represents the operation types in a Sliding Sync window.

    Attributes:
        SYNC: Sets a range of entries. Clients SHOULD discard what they previous knew about
            entries in this range.
        INSERT: Sets a single entry. If the position is not empty then clients MUST move
            entries to the left or the right depending on where the closest empty space is.
        DELETE: Remove a single entry. Often comes before an INSERT to allow entries to move
            places.
        INVALIDATE: Remove a range of entries. Clients MAY persist the invalidated range for
            offline support, but they should be treated as empty when additional operations
            which concern indexes in the range arrive from the server.
    """

    SYNC: Final = "SYNC"
    INSERT: Final = "INSERT"
    DELETE: Final = "DELETE"
    INVALIDATE: Final = "INVALIDATE"


@attr.s(slots=True, frozen=True, auto_attribs=True)
class SlidingSyncResult:
    """
    The Sliding Sync result to be serialized to JSON for a response.

    Attributes:
        next_pos: The next position token in the sliding window to request (next_batch).
        lists: Sliding window API. A map of list key to list results.
        rooms: Room subscription API. A map of room ID to room subscription to room results.
        extensions: Extensions API. A map of extension key to extension results.
    """

    @attr.s(slots=True, frozen=True, auto_attribs=True)
    class RoomResult:
        """
        Attributes:
            name: Room name or calculated room name.
            avatar: Room avatar
            heroes: List of stripped membership events (containing `user_id` and optionally
                `avatar_url` and `displayname`) for the users used to calculate the room name.
            initial: Flag which is set when this is the first time the server is sending this
                data on this connection. Clients can use this flag to replace or update
                their local state. When there is an update, servers MUST omit this flag
                entirely and NOT send "initial":false as this is wasteful on bandwidth. The
                absence of this flag means 'false'.
            required_state: The current state of the room
            timeline: Latest events in the room. The last event is the most recent
            is_dm: Flag to specify whether the room is a direct-message room (most likely
                between two people).
            invite_state: Stripped state events. Same as `rooms.invite.$room_id.invite_state`
                in sync v2, absent on joined/left rooms
            prev_batch: A token that can be passed as a start parameter to the
                `/rooms/<room_id>/messages` API to retrieve earlier messages.
            limited: True if their are more events than fit between the given position and now.
                Sync again to get more.
            joined_count: The number of users with membership of join, including the client's
                own user ID. (same as sync `v2 m.joined_member_count`)
            invited_count: The number of users with membership of invite. (same as sync v2
                `m.invited_member_count`)
            notification_count: The total number of unread notifications for this room. (same
                as sync v2)
            highlight_count: The number of unread notifications for this room with the highlight
                flag set. (same as sync v2)
            num_live: The number of timeline events which have just occurred and are not historical.
                The last N events are 'live' and should be treated as such. This is mostly
                useful to determine whether a given @mention event should make a noise or not.
                Clients cannot rely solely on the absence of `initial: true` to determine live
                events because if a room not in the sliding window bumps into the window because
                of an @mention it will have `initial: true` yet contain a single live event
                (with potentially other old events in the timeline).
        """

        name: str
        avatar: Optional[str]
        heroes: Optional[List[EventBase]]
        initial: bool
        required_state: List[EventBase]
        timeline: List[EventBase]
        is_dm: bool
        invite_state: List[EventBase]
        prev_batch: StreamToken
        limited: bool
        joined_count: int
        invited_count: int
        notification_count: int
        highlight_count: int
        num_live: int

    @attr.s(slots=True, frozen=True, auto_attribs=True)
    class SlidingWindowList:
        """
        Attributes:
            count: The total number of entries in the list. Always present if this list
                is.
            ops: The sliding list operations to perform.
        """

        @attr.s(slots=True, frozen=True, auto_attribs=True)
        class Operation:
            """
            Attributes:
                op: The operation type to perform.
                range: Which index positions are affected by this operation. These are
                    both inclusive.
                room_ids: Which room IDs are affected by this operation. These IDs match
                    up to the positions in the `range`, so the last room ID in this list
                    matches the 9th index. The room data is held in a separate object.
            """

            op: OperationType
            range: Tuple[int, int]
            room_ids: List[str]

        count: int
        ops: List[Operation]

    next_pos: StreamToken
    lists: Dict[str, SlidingWindowList]
    rooms: Dict[str, RoomResult]
    extensions: JsonMapping

    def __bool__(self) -> bool:
        """Make the result appear empty if there are no updates. This is used
        to tell if the notifier needs to wait for more events when polling for
        events.
        """
        return bool(self.lists or self.rooms or self.extensions)

    @staticmethod
    def empty(next_pos: StreamToken) -> "SlidingSyncResult":
        "Return a new empty result"
        return SlidingSyncResult(
            next_pos=next_pos,
            lists={},
            rooms={},
            extensions={},
        )
