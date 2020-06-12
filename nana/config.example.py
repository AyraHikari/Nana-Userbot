# Buat file config.py baru dalam dir dan impor yang sama, kemudian perpanjang kelas ini.
class Config(object):
	LOGGER = True
	
	# Must be filled!
	# Register here: https://my.telegram.org/apps
	api_id = 12345
	api_hash = "123456789abcdefghijklmnopqrstuvw"
	DATABASE_URL = "postgres://username:password@localhost:5432/database" # Your database URL

	# Version
	lang_code = "en" # Your language code
	device_model = "PC" # Device model
	system_version = "Linux" # OS system type

	# Required for some features
	Command = ["!", "."] # Insert command prefix, if you insert "!" then you can do !ping
	# WORKER must be int (number)
	NANA_WORKER = 8
	# If True, send notification to user if Official branch has new update after running bot
	REMINDER_UPDATE = True

	# APIs token
	thumbnail_API = "" # Register free here: https://thumbnail.ws/
	screenshotlayer_API = "" # Register free here: https://screenshotlayer.com/
	lydia_API = ""

	# Load or no load plugins
	# userbot
	USERBOT_LOAD = []
	USERBOT_NOLOAD = []

	# Fill this if you want to login using session code, else leave it blank
	USERBOT_SESSION = ""

	# Google drive API, open client_secrets.json file, copy all text, and paste into """{THIS IS API}"""
	#   If you dont have, leave it blank!
	GOOGLE_API_TEXT = """Replace this text with your API"""

	# Bitly API, register at https://dev.bitly.com/my_apps.html
	BITLY_API = ""

	# Pass True if you want to use test mode
	TEST_MODE = False
	

class Production(Config):
	LOGGER = False


class Development(Config):
	LOGGER = True
