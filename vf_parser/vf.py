#!/usr/bin/python3
from urllib import request
from lxml import etree
import re
import tempfile
import threading
import queue
import gzip
import os

class VF:
	BUFF_SIZE = 4096
	MAX_THREADS = 5
	URL_FNAME_RE = re.compile(r'(\w+\.xml)\.gz')
	DEBUG = True

	def __init__(self, link_file, output, xsl):
		self.link_file = link_file
		self.xsl = xsl
		self.output_directory = output
		self.file_queue = queue.Queue(maxsize=VF.MAX_THREADS * 4)
		self.big_file_queue = queue.Queue()
		self.threads = []

		if not os.path.exists(self.output_directory):
			os.makedirs(self.output_directory)

	def isdone(self, outfile):
		return os.path.exists(self.output_directory + '/' + outfile)

	def thread_process(self):
		while True:
			data = self.file_queue.get()
			if data is None:
				break

			fname1 = fname2 = None

			try:
				fname1 = self.download_file(data[0])

				if os.path.getsize(fname1) > 10 * 1024 * 1024: # bigger than 10MB -> leave it for later
					self.big_file_queue.put((fname1, data[1]))
					if VF.DEBUG:
						print('skipping ' + fname1 + ' for now, because it\'s too big')

					continue

				fname2 = self.uncompress(fname1)

				self.transform(fname2, data[1])

				if VF.DEBUG:
					print('done ' + data[1])
			except (MemoryError, etree.XSLTApplyError):
				if VF.DEBUG:
					print('failed ' + data[1])
			except Exception as e:
				print('error: ' + str(e))
			finally:
				self.file_queue.task_done()
				if fname1:
					os.unlink(fname1)
				if fname2:
					os.unlink(fname2)


	def download_and_parse(self):
		for i in range(VF.MAX_THREADS):
			t = threading.Thread(target=self.thread_process)
			t.start()
			self.threads.append(t)

		with open(self.link_file, 'r') as linkList:
			for line in linkList:
				m = VF.URL_FNAME_RE.search(line)
				if not m:
					continue

				outfname = m.group(1)
				if self.isdone(outfname):
					continue

				self.file_queue.put((line, outfname))

		self.file_queue.join()
		if VF.DEBUG:
			print('joined queue')

		for i in range(VF.MAX_THREADS):
			self.file_queue.put(None)
		for t in self.threads:
			t.join()

		fname2 = None

		while True:
			data = self.big_file_queue.get(False)
			if not data:
				break

			try:
				fname2 = self.uncompress(data[0])
				self.transform(fname2, data[1])

				if VF.DEBUG:
					print('done ' + data[1])
			except etree.XSLTApplyError:
				if VF.DEBUG:
					print('failed ' + data[1])
			except Exception as e:
				print('error: ' + str(e))
			finally:
				self.big_file_queue.task_done()
				os.unlink(data[0])
				if fname2:
					os.unlink(fname2)

	def download_file(self, address):
		with request.urlopen(address) as sock:
			with tempfile.NamedTemporaryFile('wb', delete=False) as writeF:
				while True:
					data = sock.read(VF.BUFF_SIZE)
					if not data:
						break

					writeF.write(data)

				return writeF.name

		raise Exception('Failed to download ' + address)

	def uncompress(self, fileName):
		with gzip.open(fileName) as gzf:
			with tempfile.NamedTemporaryFile('wb', delete=False) as writeF:
				while True:
					data = gzf.read(VF.BUFF_SIZE)
					if not data:
						break

					writeF.write(data)

				return writeF.name

		raise Exception('Failed to uncompress ' + fileName)

	def transform(self, inputFile, outputFile):
		xml = etree.parse(inputFile)
		xslt = etree.parse(self.xsl)
		doTransform = etree.XSLT(xslt)
		newdom = doTransform(xml)
		with open(self.output_directory + '/' + outputFile, 'wb') as wr:
			wr.write( etree.tostring(newdom, pretty_print=True, encoding='utf-8') )