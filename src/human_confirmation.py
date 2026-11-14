"""Deterministic human-in-the-loop selection contract: select -> edit -> confirm.

No direct host action, API request, deployment, or sending occurs here.
"""
from __future__ import annotations
import json


def new_review(items: list[dict]) -> dict:
    if not isinstance(items,list) or not items or len(items)>15:
        raise ValueError("1–15 confirmation choices required")
    ids = [i.get("id") for i in items if isinstance(i,dict)]
    if len(ids)!=len(items) or len(set(ids))!=len(ids) or any(
        not isinstance(i.get("label"),str) or not i["label"].strip()
        or not isinstance(i.get("proposed_text"),str)
        or not i["proposed_text"].strip() or len(i["proposed_text"])>3000
        for i in items):
        raise ValueError("each choice needs a label and editable proposed text")
    return {"status":"AWAITING_SELECTION","items":items,"selected_id":None,
            "editable_text":"","sent":False,"approval_granted":False,
            "explicit_confirmation_received":False}


def select(state:dict, choice_id:str) -> dict:
    options = [i for i in state["items"] if i["id"]==choice_id]
    if len(options)!=1:
        raise ValueError("unknown choice")
    return {**state,"selected_id":choice_id,
            "editable_text":options[0]["proposed_text"],
            "status":"DRAFT_EDITABLE_NOT_SENT",
            "sent":False,"approval_granted":False,
            "explicit_confirmation_received":False}


def edit(state:dict, text:str) -> dict:
    if state.get("status")!="DRAFT_EDITABLE_NOT_SENT" or (
        not isinstance(text,str) or len(text)>3000):
        raise ValueError("choose first, then edit a bounded draft")
    return {**state,"editable_text":text,"sent":False,
            "explicit_confirmation_received":False,"approval_granted":False}


def confirm(state:dict, explicit_user_click:bool) -> dict:
    if state.get("status")!="DRAFT_EDITABLE_NOT_SENT" or (
        not explicit_user_click or not isinstance(state.get("editable_text"),str)
        or not state["editable_text"].strip()):
        raise ValueError("explicit confirm action and nonblank editable text required")
    # A request draft is returned, not transmitted; execution/approval still separate.
    return {**state,"status":"CONFIRMED_TEXT_ONLY_NOT_TRANSMITTED",
            "explicit_confirmation_received":True,"sent":False,
            "approval_granted":False,
            "confirmed_text":state["editable_text"]}


def response_protocol() -> dict:
    return {"control_order":["select_choice","edit_text","review","explicit_confirm"],
            "on_select_auto_send":False,"on_select_auto_approve":False,
            "editable_after_selection":True,"user_can_cancel":True,
            "fallback":"提供可複製且可自由修改的完整選項文字，不自動傳送。",
            "transmission_requires_separate_explicit_action":True}
