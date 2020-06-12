

INMSGID = ""
async def inline_engine(msgid):
	global INMSGID
	INMSGID = msgid

async def clean_inline_engine():
	global INMSGID
	INMSGID = ""