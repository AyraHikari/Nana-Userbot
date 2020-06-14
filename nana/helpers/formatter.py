import math

def time_formatter(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	tmp = (
		((str(days) + " day(s), ") if days else "") +
		((str(hours) + " hour(s), ") if hours else "") +
		((str(minutes) + " minute(s), ") if minutes else "") +
		((str(seconds) + " second(s), ") if seconds else "")
	)
	return tmp[:-2]

def time_parser(start, end):
	time_end = end - start
	month = time_end // 2678400
	days = time_end // 86400
	hours = time_end // 3600 % 24
	minutes = time_end // 60 % 60
	seconds = time_end % 60
	times = ""
	if month:
		times += "{} month, ".format(month)
	if days:
		times += "{} days, ".format(days)
	if hours:
		times += "{} hours, ".format(hours)
	if minutes:
		times += "{} minutes, ".format(minutes)
	if seconds:
		times += "{} seconds".format(seconds)
	if times == "":
		times = "{} miliseconds".format(time_end)
	return times

def time_parser_int(time_end):
	month = time_end // 2678400
	days = time_end // 86400
	hours = time_end // 3600 % 24
	minutes = time_end // 60 % 60
	seconds = time_end % 60
	times = ""
	if month:
		times += "{} month, ".format(month)
	if days:
		times += "{} days, ".format(days)
	if hours:
		times += "{} hours, ".format(hours)
	if minutes:
		times += "{} minutes, ".format(minutes)
	if seconds:
		times += "{} seconds".format(seconds)
	if times == "":
		times = "{} miliseconds".format(time_end)
	return times

def convert_size(size_bytes):
	if size_bytes == 0:
		return "0B"
	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	i = int(math.floor(math.log(size_bytes, 1024)))
	p = math.pow(1024, i)
	s = round(size_bytes / p, 2)
	return "%s %s" % (s, size_name[i])

def speed_convert(size):
	power = 2**10
	zero = 0
	units = {
		0: '',
		1: 'Kb/s',
		2: 'Mb/s',
		3: 'Gb/s',
		4: 'Tb/s'}
	while size > power:
		size /= power
		zero += 1
	return f"{round(size, 2)} {units[zero]}"
