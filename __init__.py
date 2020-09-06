# anki-ret_bar
# Copyright (C) 2020 Tom Z.

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


import aqt.reviewer
import typing
import time
from typing import Dict, Tuple, List, Optional
from aqt import mw, gui_hooks

# Cache pass rate for last year to not have to calculate it on every main window refresh
PR_365 : Optional[int] = None

def on_webview_will_set_content(web_content: aqt.webview.WebContent, context):
    global PR_365
                
    if not isinstance(context, aqt.deckbrowser.DeckBrowser):
        return
    
    config          = mw.addonManager.getConfig(__name__) 
    addon_package   = mw.addonManager.addonFromModule(__name__)
    
    pr_delta        = max(1, config["passrate.time_range"])
    info            = get_review_info(pr_delta)

    if info is None or len(info) == 0:
        return

    prD7            = int(info["review_pass_rate"])

    if config["show.last_year"] and not PR_365:
        info        = get_review_info(365)
        prD365      = int(info["review_pass_rate"])

        if info["all_wrong"] + info["all_correct"] > 500:
            PR_365 = prD365
    else:
        prD365      = PR_365

    cf_bg           = config["bar.background"]
    cf_fg           = config["bar.foreground"]


    web_content.head += f"""
        <style>
            .tr_pr {{
                display: inline-block; 
                height: 16px; 
                padding: 3px 0; 
                line-height: 1em;
                font-weight: bold; 
                text-align: center;
                color: {cf_fg};
            }}
            .tr_pr_left {{
                background: {cf_bg};
                border-bottom-left-radius: 6px; 
                border-top-left-radius: 6px;
                float: left;
            }}
            .tr_pr_right {{
                background: grey;
                border-bottom-right-radius: 6px; 
                border-top-right-radius: 6px;
            }}
            .tr_pr_left.pr_100 {{
                border-top-right-radius: 6px; 
                border-bottom-right-radius: 6px;
            }}
        </style>

    """

    pr_lbl = f"last {pr_delta} days" if pr_delta > 1 else "today"

    pr_year = ""
    if config["show.last_year"]:
        pr_year = f"""
                <div style='width: 600px; text-align: left;'>
                    <div style='width: 300px; display: inline-block; box-sizing: border-box; white-space: nowrap; text-align: center; margin: 10px 0 30px 0; zoom: 0.8;'>
                        <div style='margin-bottom: 6px; font-weight: bold; text-align: left; font-variant: all-petite-caps; opacity: 0.6;'>Pass Rate, last 365 days</div>
                        <div class='tr_pr tr_pr_left pr_{int(prD365)}' style='width: {prD365}%'><span style='vertical-align: middle;'>{prD365}%</span></div> 
                        <div class='tr_pr tr_pr_right' style='width: {100-prD365}%'><span style='vertical-align: middle;'>&nbsp;</span></div> 
                    </div> 
                </div> 
            """

    web_content.body += f"""<script>
        (() => {{
            let c = document.getElementsByTagName('center')[0];
            let html = `
                <div style='width: 600px; box-sizing: border-box; white-space: nowrap; text-align: center; margin: 30px 0 0 0;'>
                    <div style='margin-bottom: 6px; font-weight: bold; text-align: left; font-variant: all-petite-caps; opacity: 0.6;'>Pass Rate, {pr_lbl}</div>
                    <div class='tr_pr tr_pr_left pr_{int(prD7)}' style='width: {prD7}%'><span style='vertical-align: middle;'>{prD7}%</span></div> 
                    <div class='tr_pr tr_pr_right' style='width: {100-prD7}%;'><span style='vertical-align: middle;'>&nbsp;</span></div> 
                </div> 
                {pr_year}
            `;
            c.innerHTML += html; 
        }})();
        </script>"""


def get_review_info(delta_days: int) -> Dict[str, float]:
    """  """

    rid             = nid_midnight(delta_days)
    res             = mw.col.db.all(f"select ease, type from revlog where id > {rid}")
    if len(res) == 0:
        return None
    idict           = {}

    review_correct, review_wrong, all_correct, all_wrong = _rev_counts(res) 

    if review_wrong + review_correct == 0:
        idict["review_pass_rate"] = 0
    else:
        idict["review_pass_rate"] = round(review_correct * 100.0 / (review_wrong + review_correct), 1)

    idict["all_pass_rate"]    = round(all_correct * 100.0 / (all_wrong + all_correct), 1)
    idict["review_correct"]         = review_correct
    idict["review_wrong"]           = review_wrong
    idict["all_wrong"]              = all_wrong
    idict["all_correct"]            = all_correct

    return idict

def nid_now() -> int:
    return int(time.time()*1000)


def nid_midnight(delta_n: int) -> int:
    """
    Returns the nid for the nth midnight before now.
    E.g. delta_n = 1 means last midnight.
    """
    now             = nid_now() 
    days, rem       = divmod(now, 24*3600* 1000)
    last_midnight   = now - rem

    return last_midnight - 24*3600*1000*(delta_n - 1)

def _rev_counts(revs: List[Tuple[int, int]]) -> Tuple[int, int, int, int]:
    review_correct  = 0
    review_wrong    = 0
    all_correct     = 0
    all_wrong       = 0
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