import urllib.request
import pyforms
from pyforms import BaseWidget
from pyforms.Controls import ControlText
from pyforms.Controls import ControlButton

class dbSearcher(BaseWidget):
	def __init__(self):
		super(dbSearcher,self).__init__('Aseem\'s DB')
		self._query = ControlText('Query')
		self._search = ControlButton('Search')
		self._search.value = self.__searchAction

		self.formset = ['_query','_search',' ']

	def __searchAction(self):
		print('search')

if __name__=="__main__": pyforms.start_app(dbSearcher)