import gzip.open
from tempfile import NamedTemporaryFile
from urllib import request

from .base import Settings

def download_file(address):
	with request.urlopen(address) as sock:
		with NamedTemporaryFile('wb', delete=False) as writeF:
			while True:
				data = sock.read(Settings.BUFF_SIZE)
				if not data:
					break

				writeF.write(data)

			return writeF.name

	raise Exception('Failed to download ' + address)

def uncompress(fileName):
	with gzip.open(fileName) as gzf:
		with NamedTemporaryFile('wb', delete=False) as writeF:
			while True:
				data = gzf.read(Settings.BUFF_SIZE)
				if not data:
					break

				writeF.write(data)

			return writeF.name

	raise Exception('Failed to uncompress ' + fileName)
