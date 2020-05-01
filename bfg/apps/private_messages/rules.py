# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import rules

from bfg.apps.communities.rules import is_member

rules.add_perm("private_messages.create_message", is_member)
