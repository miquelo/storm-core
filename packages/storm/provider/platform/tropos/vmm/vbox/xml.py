#
# This file is part of STORM-CORE.
#
# STORM-CORE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# STORM-CORE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with STORM-CORE.  If not, see <http://www.gnu.org/licenses/>.
#

# TODO Fix standard failure for processing instructions
# PITarget accepts (('X' | 'x') ('M' | 'm') ('L' | 'l')) here, but it won't
# http://www.w3.org/TR/REC-xml/#sec-pi

import io

class QName:

	def __init__(self, local_name, prefix=None):
	
		self.__local_name = local_name
		self.__prefix = prefix
		
	def __eq__(self, other):
	
		same_name = self.local_name == other.local_name
		same_prefix = self.prefix == other.prefix
		return same_name and same_prefix
		
	def __str__(self):
	
		if self.__prefix is None:
			return self.__local_name
		return "{}:{}".format(self.__prefix, self.__local_name)
		
	@property
	def local_name(self):
	
		return self.__local_name
		
	@property
	def prefix(self):
	
		return self.__prefix
		
class Attribute:

	def __init__(self, name, value):
	
		self.__name = name
		self.__value = value
		
	def __str__(self):
	
		return "{}=\"{}\"".format(self.__name, self.__value)
		
	@property
	def name(self):
	
		return self.__name
		
	@property
	def value(self):
	
		return self.__value
		
class Reader:

	def __init__(self, src):
	
		self.__source = src
		
	def __iter__(self):
	
		c = self.read(1)
		while len(c) > 0:
			yield from self.next(c)
			c = self.read(1)
			
	# Protected
	def read(self, count):
	
		v = self.__source.read(count)
		# print("{}.read({}) -> [{}]".format(type(self), count, v))
		if type(v) == str:
			return v
		# TODO Improve decoding operation
		if type(v) == bytes:
			return v.decode("UTF-8")
		raise Exception("Invalid read value type")
		
	def is_fragment(self):
	
		return False
		
	def is_element(self):
	
		return False
		
	def is_proc_instr(self):
	
		return False
		
	def is_text(self):
	
		return False
		
class ComplexReader(Reader):

	def __init__(self, src, elem_closed_fn):
	
		super().__init__(src)
		self.__elem_closed_fn = elem_closed_fn
		self.__name = None
		self.__prefix = None
		self.__attrs = []
		self.__attr_name = None
		self.__attr_prefix = None
		self.__attr_value = None
		self.__next = self.__next_content
		
	def __read_lt_fn(self):
	
		self.__next = self.__next_lt
		
	def __read_amp_fn(self):
	
		raise Exception("Not supported")
		
	def __next_content(self, c):
	
		if c == "<":
			self.__read_lt_fn()
			yield from ()
		elif c == "&":
			self.__read_amp_fn()
			yield from ()
		else:
			yield TextReader(self, c, self.__read_lt_fn, self.__read_amp_fn)
		
	def __next_lt(self, c):
	
		if c == "!":
			raise Exception("Not supported")
		if c == "?":
			self.__next = self.__next_pi_name_first
			yield from ()
		elif c == "/":
			self.__next = self.__next_elem_end_name_first
			yield from ()
		elif c.isalnum():
			self.__name = io.StringIO()
			self.__name.write(c)
			self.__next = self.__next_elem_name
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
		
	def __next_pi_name_first(self, c):
	
		if c.isalnum():
			self.__name = io.StringIO()
			self.__name.write(c)
			self.__next = self.__next_pi_name
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
		
	def __next_pi_name(self, c):
	
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__name.write(c)
			yield from ()
		elif c == ":":
			self.__prefix = self.__name
			self.__next = self.__next_pi_lname_first
			yield from ()
		elif c == "?":
			self.__next = self.__next_pi_name_quest
			yield from ()
		elif c.isspace():
			self.__next = self.__next_content
			name = QName(self.__name.getvalue())
			yield ProcessingInstructionReader(self, name, c)
		
	def __next_pi_lname_first(self, c):
	
		if c.isalnum():
			self.__name = io.StringIO()
			self.__name.write(c)
			self.__next = self.__next_pi_lname
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
		
	def __next_pi_lname(self, c):
	
		if c == ":":
			raise Exception("Illegal character '{}'".format(c))
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__name.write(c)
			yield from ()
		elif c == "?":
			self.__next = self.__next_pi_name_quest
			yield from ()
		elif c.isspace():
			self.__next = self.__next_content
			name = QName(self.__name.getvalue(), self.__prefix.getvalue())
			yield ProcessingInstructionReader(self, name, c)
		
	def __next_pi_name_quest(self, c):
	
		if c != ">":
			raise Exception("Illegal character '{}'".format(c))
		self.__next = self.__next_content
		name = QName(self.__name.getvalue(), self.__prefix.getvalue())
		yield ProcessingInstructionReader(self, name, None)
		
	def __next_elem_name(self, c):
	
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__name.write(c)
			yield from ()
		elif c == ">":
			self.__next = self.__next_content
			name = QName(self.__name.getvalue())
			yield ElementReader(self, name, [], False)
		elif c == ":":
			self.__prefix = self.__name
			self.__next = self.__next_elem_lname_first
			yield from ()
		elif c == "/":
			self.__next = self.__next_elem_name_slash
			yield from ()
		elif c.isspace():
			self.__next = self.__next_elem_content
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_elem_lname_first(self, c):
	
		if c.isalnum():
			self.__name = io.StringIO()
			self.__name.write(c)
			self.__next = self.__next_elem_lname
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
		
	def __next_elem_lname(self, c):
	
		if c == ":":
			raise Exception("Illegal character '{}'".format(c))
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__name.write(c)
			yield from ()
		elif c == ">":
			self.__next = self.__next_content
			name = QName(self.__name.getvalue(), self.__prefix.getvalue())
			yield ElementReader(self, name, [], False)
		elif c == "/":
			self.__next = self.__next_elem_name_slash
			yield from ()
		elif c.isspace():
			self.__next = self.__next_elem_content
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
		
	def __next_elem_name_slash(self, c):
	
		if c != ">":
			raise Exception("Illegal character '{}'".format(c))
		self.__next = self.__next_content
		name = QName(self.__name.getvalue(), self.__prefix.getvalue())
		yield ElementReader(self, name, [], True)
		
	def __next_elem_content(self, c):
	
		if not c.isspace():
			if c == "/":
				self.__next = self.__next_elem_content_slash
				yield from ()
			elif c == ">":
				self.__next = self.__next_content
				name = QName(self.__name.getvalue(), self.__prefix.getvalue())
				yield ElementReader(self, name, self.__attrs, False)
				self.__attrs = []
			elif c.isalnum():
				self.__attr_name = io.StringIO()
				self.__attr_name.write(c)
				self.__next = self.__next_attr_name
				yield from ()
			else:
				raise Exception("Illegal character '{}'".format(c))
		else:
			yield from ()
				
	def __next_elem_content_slash(self, c):
	
		if c != ">":
			raise Exception("Illegal character '{}'".format(c))
		self.__next = self.__next_content
		name = QName(self.__name.getvalue(), self.__prefix.getvalue())
		yield ElementReader(self, name, self.__attrs, True)
		self.__attrs = []
		
	def __next_attr_name(self, c):
	
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__attr_name.write(c)
			yield from ()
		elif c == ":":
			self.__attr_prefix = self.__attr_name
			self.__next = self.__next_attr_lname_first
			yield from ()
		elif c == "=":
			self.__next = self.__next_attr_value_content
			yield from ()
		elif c.isspace():
			self.__next = self.__next_attr_name_content
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_attr_lname_first(self, c):
	
		if c.isalnum():
			self.__attr_name = io.StringIO()
			self.__attr_name.write(c)
			self.__next = self.__next_attr_lname
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_attr_lname(self, c):
	
		if c == ":":
			raise Exception("Illegal character '{}'".format(c))
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__attr_name.write(c)
			yield from ()
		elif c == "=":
			self.__next = self.__next_attr_value_content
			yield from ()
		elif c.isspace():
			self.__next = self.__next_attr_name_content
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_attr_name_content(self, c):
	
		if not c.isspace():
			if c == "=":
				self.__next = self.__next_attr_value_content
				yield from ()
			else:
				raise Exception("Illegal character '{}'".format(c))
		else:
			yield from ()
			
	def __next_attr_value_content(self, c):
	
		if not c.isspace():
			if c == "\"":
				self.__attr_value = io.StringIO()
				self.__next = self.__next_attr_value
				yield from ()
			else:
				raise Exception("Illegal character '{}'".format(c))
		else:
			yield from ()
			
	def __next_attr_value(self, c):
	
		if c == "\"":
			self.__next = self.__next_attr_value_end
			name = QName(
				self.__attr_name.getvalue(),
				self.__attr_prefix.getvalue()
			)
			self.__attrs.append(Attribute(name, self.__attr_value.getvalue()))
			yield from ()
		else:
			self.__attr_value.write(c)
			yield from ()
			
	def __next_attr_value_end(self, c):
	
		if c == ">":
			self.__next = self.__next_content
			name = QName(self.__name.getvalue(), self.__prefix.getvalue())
			yield ElementReader(self, name, self.__attrs, False)
		elif c == "/":
			self.__next = self.__next_elem_content_slash
			yield from ()
		elif c.isspace():
			self.__next = self.__next_elem_content
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_elem_end_name_first(self, c):
	
		if c.isalnum():
			self.__next = self.__next_elem_end_name
			self.__name = io.StringIO()
			self.__name.write(c)
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_elem_end_name(self, c):
	
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__name.write(c)
			yield from ()
		elif c == ":":
			self.__next = self.__next_elem_end_lname_first
			self.__prefix = self.__name
			yield from ()
		elif c == ">":
			self.__next = self.__next_content
			self.__elem_closed_fn(QName(self.__name.getvalue()))
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_elem_end_lname_first(self, c):
	
		if c.isalnum():
			self.__next = self.__next_elem_end_lname
			self.__name = io.StringIO()
			self.__name.write(c)
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	def __next_elem_end_lname(self, c):
	
		if c == ":":
			raise Exception("Illegal character '{}'".format(c))
		if c.isalnum() or c in ( "+", "-", "_" ):
			self.__name.write(c)
			yield from ()
		elif c == ">":
			self.__next = self.__next_content
			name = QName(self.__name.getvalue(), self.__prefix.getvalue())
			self.__elem_closed_fn(name)
			yield from ()
		else:
			raise Exception("Illegal character '{}'".format(c))
			
	# Protected
	def next(self, c):
	
		yield from self.__next(c)
		
	def ignore(self):
	
		for item in self:
			item.ignore()
			
class FragmentReader(ComplexReader):

	def __init__(self, src):
	
		super().__init__(src, self.__elem_closed_fn)
		
	def __elem_closed_fn(self, name):
	
		raise Exception("Misplaced element closing '{}'".format(name))
		
	def is_fragment(self):
	
		return True
		
class ElementReader(ComplexReader):

	def __init__(self, src, name, attrs, closed):
	
		super().__init__(src, self.__elem_closed_fn)
		self.__name = name
		self.__attrs = attrs
		if closed:
			self.__read = self.__read_terminated
		else:
			self.__read = self.__read_default
			
	def __elem_closed_fn(self, name):
	
		if name == self.__name:
			self.__read = self.__read_terminated
		else:
			raise Exception("Misplaced element ending '{}'".format(name))
		
	def __read_terminated(self, count):
	
		return ""
		
	def __read_default(self, count):
	
		return super().read(count)
		
	# Protected
	def read(self, count):
	
		return self.__read(count)
		
	def is_element(self):
	
		return True
		
	def name(self):
	
		return self.__name
		
	def attributes(self):
	
		return self.__attrs
		
class ProcessingInstructionReader(Reader):

	def __init__(self, src, name, first_c):
	
		super().__init__(src)
		self.__name = name
		self.__first_c = first_c
		if self.__first_c is None:
			self.__read = self.__read_terminated
		else:
			self.__read = self.__read_first
		self.__next = self.__next_content
		
	def __read_first(self, count):
	
		self.__read = self.__read_default
		
		text = io.StringIO()
		text.write(self.__first_c)
		if count > 1:
			text.write(self.read(count - 1))
		return text.getvalue()
		
	def __read_default(self, count):
	
		return super().read(count)
		
	def __read_terminated(self, count):
	
		return ""
		
	def __next_content(self, c):
	
		if c == "?":
			self.__next = self.__next_quest
			yield from ()
		else:
			yield c
			
	def __next_quest(self, c):
	
		if c == ">":
			self.__read = self.__read_terminated
			yield from ()
		else:
			self.__next = self.__next_content
			yield "?"
			yield c
			
	# Protected
	def read(self, count):
	
		return self.__read(count)
		
	# Protected
	def next(self, c):
	
		yield from self.__next(c)
		
	def is_proc_instr(self):
	
		return True
		
	def ignore(self):
	
		for c in self:
			pass
			
	def name(self):
	
		return self.__name
		
class TextReader(Reader):

	def __init__(self, src, first_c, read_lt_fn, read_amp_fn):
	
		super().__init__(src)
		self.__first_c = first_c
		self.__read_lt_fn = read_lt_fn
		self.__read_amp_fn = read_amp_fn
		self.__read = self.__read_first
		
	def __read_first(self, count):
	
		self.__read = self.__read_default
		
		text = io.StringIO()
		text.write(self.__first_c)
		if count > 1:
			text.write(self.read(count - 1))
		return text.getvalue()
		
	def __read_default(self, count):
	
		return super().read(count)
		
	def __read_terminated(self, count):
	
		return ""
		
	def __next(self, c):
	
		if c == ">":
			raise Exception("Illegal character '{}'".format(c))
		if c == "<":
			self.__read = self.__read_terminated
			self.__read_lt_fn()
		elif c == "&":
			self.__read = self.__read_terminated
			self.__read_amp_fn()
		else:
			yield c
			
	# Protected
	def read(self, count):
	
		return self.__read(count)
		
	# Protected
	def next(self, c):
	
		yield from self.__next(c)
		
	def is_text(self):
	
		return True
		
	def ignore(self):
	
		for c in self:
			pass
			
class Writer:

	def __init__(self, tgt):
	
		self.__target = tgt
		
	# Protected
	def write(self, text):
	
		self.__target.write(text)
		
class ComplexWriter(Writer):

	def __init__(self, tgt, write_content_fn):
	
		super().__init__(tgt)
		self.__write_content_fn = write_content_fn
				
	def element(self, name, attrs=None):
	
		self.__write_content_fn()
		self.write("<")
		self.write(str(name))
		if attrs is not None:
			for attr in attrs:
				self.write(" ")
				self.write(str(attr))
		return ElementWriter(self, name)
		
	def processing_instruction(self, name):
	
		self.__write_content_fn()
		self.write("<?")
		self.write(str(name))
		return ProcessingInstructionWriter(self)
		
	def text(self):
	
		self.__write_content_fn()
		return TextWriter(self)
		
class FragmentWriter(ComplexWriter):

	def __init__(self, tgt):
	
		super().__init__(tgt, self.__write_content_fn)
		
	def __write_content_fn(self):
	
		pass
		
class ElementWriter(ComplexWriter):

	def __init__(self, tgt, name):
	
		super().__init__(tgt, self.__write_content_fn)
		self.__name = name
		self.__write_content = self.__write_content_begin
		self.__close = self.__close_empty
		
	def __write_content_fn(self):
	
		self.__write_content()
		
	def __write_content_begin(self):
	
		self.write(">")
		self.__write_content = self.__write_content_default
		self.__close = self.__close_content
		
	def __write_content_default(self):
	
		pass
		
	def __close_empty(self):
	
		self.write("/>")
		
	def __close_content(self):
	
		self.write("</")
		self.write(str(self.__name))
		self.write(">")
		
	def __raise_already_closed(self):
	
		raise Exception("Element already closed")
		
	def close(self):
	
		self.__close()
		self.__close = self.__raise_already_closed
		
class ProcessingInstructionWriter(Writer):

	def __init__(self, tgt):
	
		super().__init__(tgt)
		self.__write_content = self.__write_content_begin
		self.__close = self.__close_default
		
	def __write_content_begin(self):
	
		self.write(" ")
		self.__write_content = self.__write_content_default
		
	def __write_content_default(self):
	
		pass
		
	def __close_default(self):
	
		self.write("?>")
		
	def __raise_already_closed(self):
	
		raise Exception("Processing instruction already closed")
		
	def append(self, text):
	
		self.__write_content()
		self.write(text)
		
	def close(self):
	
		self.__close()
		self.__write_content = self.__raise_already_closed
		self.__close = self.__raise_already_closed
		
class TextWriter(Writer):

	def __init__(self, tgt):
	
		super().__init__(tgt)
		
	def append(self, text):
	
		self.write(text)

