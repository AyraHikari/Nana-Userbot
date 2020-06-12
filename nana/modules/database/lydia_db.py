import os
import time
import requests
import json
import threading

from sqlalchemy import Column, UnicodeText, Integer, String, Boolean
from nana import BASE, SESSION
from nana.helpers.msg_types import Types

class LydiaAI(BASE):
	__tablename__ = "self_lydia"
	user_id = Column(Integer, primary_key=True)
	is_enable = Column(Boolean, default=False)

	def __init__(self, user_id):
		self.user_id = user_id

	def __repr__(self):
		return "<Lydia %s>" % self.user_id

LydiaAI.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def set_lydia(user_id, enable):
	with INSERTION_LOCK:
		# global LydiaAI
		curr = SESSION.query(LydiaAI).get(int(user_id))
		if not curr:
			curr = LydiaAI(int(user_id))
		curr.is_enable = enable
		SESSION.add(curr)
		SESSION.commit()
		# LydiaAI.append(user_id)

def get_lydia(user_id):
	try:
		# return LydiaAI
		check = SESSION.query(LydiaAI).get(int(user_id))
		if check:
			return check.is_enable
		return False
	finally:
		SESSION.close()

'''
def __load_afk():
	global MY_AFK
	try:
		MY_AFK = {}
		qall = SESSION.query(AFK).all()
		for x in qall:
			MY_AFK[int(x.user_id)] = {"afk": x.is_afk, "reason": x.reason}
	finally:
		SESSION.close()

__load_afk()
'''