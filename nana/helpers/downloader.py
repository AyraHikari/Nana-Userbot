import time, os

from nana.helpers import time_formatter, time_parser_int, time_parser, convert_size
from pyDownload import Downloader
from pySmartDL import SmartDL


async def download_url(url, file_name):
	start = int(time.time())
	downloader = Downloader(url=url)
	end = int(time.time())
	times = time_parser(start, end)
	downlaoded = f"⬇️ Downloaded `{file_name}` in {times}"
	downlaoded += "\n🗂 File name: {}".format(file_name)
	size = os.path.getsize(downloader.file_name)
	if size > 1024000000:
		file_size = round(size / 1024000000, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " GB`\n"
	elif size > 1024000 and size < 1024000000:
		file_size = round(size / 1024000, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " MB`\n"
	elif size > 1024 and size < 1024000:
		file_size = round(size / 1024, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " KB`\n"
	elif size < 1024:
		file_size = round(size, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " Byte`\n"

	try:
		os.rename(downloader.file_name, "nana/downloads/" + file_name)
	except OSError:
		return False, "Failed to download file\nInvaild file name!"
	return True, downlaoded


async def download_url_multi(url, file_name):
	start = int(time.time())
	downloader = SmartDL(url, "nana/downloads/" + file_name, progress_bar=False)
	try:
		downloader.start(blocking=False)
	except Exception as e:
		return False, str(e)
	while not downloader.isFinished() and downloader.get_status() == "downloading":
		eta = round(downloader.get_eta())
		await asyncio.sleep(eta if eta else 1)
		if status == "Combining":
			wait = round(downloader.get_eta())
			await asyncio.sleep(wait)
	end = int(time.time())
	times = time_parser(start, end)
	downlaoded = f"⬇️ Downloaded `{file_name}` in {times}"
	downlaoded += "\n🗂 File name: {}".format(file_name)
	size = os.path.getsize(downloader.file_name)
	if size > 1024000000:
		file_size = round(size / 1024000000, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " GB`\n"
	elif size > 1024000 and size < 1024000000:
		file_size = round(size / 1024000, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " MB`\n"
	elif size > 1024 and size < 1024000:
		file_size = round(size / 1024, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " KB`\n"
	elif size < 1024:
		file_size = round(size, 3)
		downlaoded += "\n💿 File size: `" + str(file_size) + " Byte`\n"

	return True, downlaoded

