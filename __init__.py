# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import aqt
import typing
import time
from typing import Dict, Tuple, List, Optional
from aqt import mw, gui_hooks


def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):

    if not isinstance(context, aqt.deckbrowser.DeckBrowser):
        return

    config = mw.addonManager.getConfig(__name__)

    pr_delta = max(1, config["passrate.time_range"])
    info = get_review_info(pr_delta)

    if info is None or len(info) == 0 or info["review_total"] < 5:
        return

    prD7 = int(info["review_pass_rate"])

    cf_bg = config["bar.background"]
    cf_fg = config["bar.foreground"]

    web_content.head += f"""
        <style>
            .container {{
                width: 500px;
                margin: 25px auto 0 auto;
            }}
            .title {{
                margin-bottom: 6px;
                font-weight: bold;
                font-variant: all-petite-caps;
                text-align: left;
                color: dimgray;
            }}
            .progress {{
                height: 2em;
                border-radius: 6px;
                box-sizing: border-box;
                background-color: {cf_bg};
                position: relative;
            }}
            .progress:before {{
                content: attr(data-label);
                font-size: 1.2em;
                font-weight: bold;
                position: absolute;
                text-align: center;
                left: 0;
                right: 0;
            }}
            .progress .value {{
                background-color: {cf_fg};
                border-radius: 6px;
                display: inline-block;
                height: 100%;
            }}
        </style>

    """

    pr_lbl = f"last {pr_delta} days" if pr_delta > 1 else "today"

    web_content.body += f"""
                <div class="container">
                    <div class="title">Pass Rate, {pr_lbl}</div>
                    <div class="progress" data-label="{prD7}%">
                        <span class="value" style="width:{prD7}%;"></span>
                    </div>
                </div>
            """


def get_review_info(delta_days: int) -> Dict[str, float]:

    rid = nid_midnight(delta_days)
    res = mw.col.db.all(f"select ease, type from revlog where id > {rid}")
    if len(res) == 0:
        return None
    idict = {}

    review_correct, review_wrong, all_correct, all_wrong = _rev_counts(res)

    if review_wrong + review_correct == 0:
        idict["review_pass_rate"] = 0
    else:
        idict["review_pass_rate"] = round(
            review_correct * 100.0 / (review_wrong + review_correct), 1
        )

    idict["all_pass_rate"] = round(all_correct * 100.0 / (all_wrong + all_correct), 1)
    idict["review_correct"] = review_correct
    idict["review_wrong"] = review_wrong
    idict["all_wrong"] = all_wrong
    idict["all_correct"] = all_correct
    idict["review_total"] = review_correct + review_wrong

    return idict


def nid_now() -> int:
    return int(time.time() * 1000)


def nid_midnight(delta_n: int) -> int:
    """
    Returns the nid for the nth midnight before now.
    E.g. delta_n = 1 means last midnight.
    """
    now = nid_now()
    days, rem = divmod(now, 24 * 3600 * 1000)
    last_midnight = now - rem

    return last_midnight - 24 * 3600 * 1000 * (delta_n - 1)


def _rev_counts(revs: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    review_correct = 0
    review_wrong = 0
    all_correct = 0
    all_wrong = 0
    for ease, type in revs:
        if type == 1 and ease == 1:
            review_wrong += 1
        elif type == 1:
            review_correct += 1

        if ease == 1:
            all_wrong += 1
        else:
            all_correct += 1

    return (review_correct, review_wrong, all_correct, all_wrong)


# add hook
gui_hooks.webview_will_set_content.append(on_webview_will_set_content)
