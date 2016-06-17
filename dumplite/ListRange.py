# -*- encoding: utf-8 -*-
class ListRange(list):
	def __init__(self, r=[]):
		if len(r):
			self.addRange( r )
	def addRange(self, r ):
		if r[1] <= r[0]:
			return self
		new  = ListRange()
		while len(self) > 0:
			i = self.pop(0)
			if i[0] > r[1]+1:
				self.insert(0, i)
				break
			if r[0] > i[1]+1:
				new.append(i)
				continue
			if i[0] <= r[0]:
				r[0] = i[0]
			if i[1] >= r[1]:
				r[1] = i[1]
				break
		new.append(r)
		new.extend(self)
		self[:] = new[:]
		return new

	def delRange(self, r):
		if r[1] < r[0]:
			return self
		new  = ListRange()
		while len(self) > 0:
			i = self.pop(0)
			if i[0] > r[1]+1:
				self.insert(0, i)
				break
			if r[0] > i[1]+1:
				new.append(i)
				continue
			if i[0] < r[0]:
				self.insert(0, [r[0]+1, i[1]])
				new.append([i[0], r[0]-1])
				continue
			if i[1] > r[1]:
				self.insert(0, [r[1]+1, i[1]])
				break
		new.extend(self)
		self[:] = new[:]
		return new
