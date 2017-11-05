from HTMLParser import HTMLParser

class Post:
	#class meant to store information about a given Facebook post
	#information is obtained from myHTMLParser
	def __init__(self):
		self.text = []
		self.poster = ''
		self.likes = 0
		self.datetime = ''
		self.UTC = 0
		self.reacts = {"Haha":0,"Like":0,"Love":0,"Wow":0,"Sad":0,"Pride":0,"Angry":0,"Thankful":0}
		self.type = []
		self.modStatus = 0 #0 - not mod, 1 - mod, 2 - admin

	#getter setter methods
	def getText(self):
		return self.text
	def getPoster(self):
		return self.poster
	def getLikes(self):
		return self.likes
	def getDatetime(self):
		return self.datetime
	def getUTC(self):
		return self.UTC 
	def getReacts(self):
		return self.reacts
	def getType(self):
		return self.type
	def getMod(self):
		return self.modStatus

	def setText(self, text):
		self.text += [text]
	def setPoster(self, poster):
		self.poster = poster
	def setLikes(self, likes):
		self.likes = int(likes)
	def setDatetime(self, datetime):
		self.datetime = datetime
	def setUTC(self, utc):
		self.UTC = int(utc)
	def setReacts(self,reaction, num):
		#sets a given reaction in the self.reacts dict to be a given value
		#implemented in this way because of the way myHTMLParser detects reacts
		self.reacts[reaction] = int(num)
	def setType(self,types):
		self.type += [types]
	def setMod(self,mod):
		self.modStatus = int(mod)

	#__str__() meant primarily for debugging purposes, but generally for displaying all relevant fields of a post
	def __str__(self):
		self.consolidate()
		output = ''
		output += 'Poster:\t' + self.poster
		output += '\nText:\t' + ('none' if len(self.text)==0 else str(self.text))
		output += '\nLikes:\t' + str(self.likes)
		# for react in self.reacts:
		# 	output+='\n\t'+react+' '+str(self.reacts[react])
		output += '\nreacts:\t'+str(self.reacts)
		output += '\nDate time:\t' + self.datetime + ' (%s)'%self.UTC
		for types in self.type:
			output += '\ntype:\t' + types
		output += '\nmod?:\t' + ('nah' if self.modStatus==0 else ('myeah' if self.modStatus==1 else 'admin'))
		return output+'\n'

	#series of boolean methods that are used in myHTMLParser to decide whether a field has been assigned yet
	#not robust, as it is theoretically possible for an edge case to successfully fail one of these tests
	#	despite being assigned, but not really worth worrying about
	def textNull(self):
		return len(self.text)==0
	def posterNull(self):
		return self.poster==''
	def likesNull(self):
		return self.likes == 0
	def datetimeNull(self):
		return self.datetime == ''
	def UTCNull(self):
		return self.UTC == 0
	def reactsNull(self):
		for react in self.reacts:
			if self.reacts[react]>0:
				return False
		return True
	def typeNull(self):
		return len(self.type)==0

	#a boolean method that checks whether a post is null - it doesn't check everyone of the above methods, but
	#	in principle it shouldn't have to, as several are set at the same time and even then a post without
	#	these attributes is effectively non-existant anyways
	def isNull(self):
		return self.textNull() and self.posterNull() and self.likesNull() and self.datetimeNull() and self.reactsNull()

	#method that cleans up the output of myHTMLParser, in particular merging together multiple text fields into a single string
	#	and consolidates a list of types with duplicates into a set with only unique types
	def consolidate(self):
		def joinCon(x,y):
			if x[-1].islower() or x[-1]==' ':
				return x+y
			return x+'\n'+y

		if not self.textNull():
			textFix = filter(lambda x:x!='...',self.text)
			textFix = reduce(joinCon,textFix).replace('See More','')
			textFix = textFix.replace('\x92','\'')

			self.text = textFix
		else:
			self.text = ''

		def removeCon(x,y):
			if type(x) is list:
				if x[-1]==y:
					return x
				return x+[y]
			else:
				if x==y:
					return [x]
				return [x,y]
		if len(self.type)>1:
			self.type = reduce(removeCon,self.type)
		# print self.type

class ContentProvider:
	#class that represents a poster (content provider)
	#mostly a vehicle for associated posts by a given individual
	def __init__(self,name,modStatus):
		self.name = name
		self.posts = []
		self.mod = modStatus
		self.totalLikes = 0
		self.totalReacts= {"Haha":0,"Like":0,"Love":0,"Wow":0,"Sad":0,"Pride":0,"Angry":0,"Thankful":0}
		self.totalPosts = 0

	def addPost(self, post):
		poster = post.getPoster()
		if poster != self.name:
			print 'error: name does not match that of the post\'s creator'
		else:
			self.totalPosts += 1
			self.posts += [post]
			self.totalLikes += post.getLikes()
			reacts = post.getReacts()
			for react in reacts:
				# print reacts[react]
				self.totalReacts[react]+=int(reacts[react])

	def __str__(self):
		return self.name+' '+self.totalLikes+' '+self.totalPosts

class pageAnalysis:
	#class that contains multiple analysis methods; contains an instance of myHTMLParser that is run

	def __init__(self):
		self.posters = {}
		self.allPosts = []
		self.mods = {}
		self.parser = myHTMLParser()
		self.sortedKeys = []
		self.params = []
		self.map_reduce = lambda a: reduce(lambda x,y:x+y, map(lambda z:z(a),self.params))

		self.standardDev = 0
		self.adjustment = 0

	def addPosts(self,posts):
		#this class tracks a dict of ContentProviders indexed by poster name, and this method
		#	explicitly takes in a list of Posts, which are associated with the appropriate ContentProvider,
		#	adding them when necessary

		for post in posts:
			#print post
			user = post.getPoster()
			if user not in self.posters:
				self.posters[user]=ContentProvider(post.getPoster(),post.getMod())
				self.sortedKeys+=[user]
				# print self.sortedKeys
			if post.getMod()>0:
				self.mods[user]=post.getMod()
			self.posters[user].addPost(post)
			self.allPosts+=[post]

	def run(self, file):
		#runs the instance of myHTMLParser on the text file with name specified by file

		fileToParse = open(file).read()
		self.parser.feed(fileToParse)
		posts = self.parser.postList
		self.addPosts(posts)

	def dSq(self,x,y):
		#method for calculating the d(ifference) sq(uared)

		#print x,y
		return (x-y)**2

	def standardDevPost(self,post,comparePoster=True):
		#calculates the standard deviation of all parameters of a post
		#based on the boolean value of comparePoster, it either calculates the standard deviation based on
		#	the posts made by a specific ContentProvider or by across all ContentProviders (across self.allPosts)

		if post not in self.allPosts:
			print 'come on that\'s not a real post'
		else:
			poster = post.poster
			likes = post.likes
			tReacts = reduce(lambda x,y:x+y,map(lambda z: post.reacts[z],post.reacts.keys()))
			iReacts = [post.reacts[x] for x in post.reacts.keys()]
			#print likes, tReacts, iReacts

			zScores = []
			if comparePoster:
				contentProvider = self.posters[poster]
				num = contentProvider.totalPosts-1
				if num > 0:
					avgLikes = self.getLambda(1)(poster)
					avgTotalReacts = self.getLambda(4)(poster)
					avgIndivReacts = [self.getLambda(x)(poster) for x in range(6,22,2)]

					posterPosts = contentProvider.posts
					likeSDSq = 0	#likes sum of differences squared
					tReactsSDSq = 0
					iReactsSDSq = [0 for i in range(len(post.reacts))]
					for posterPost in posterPosts:
						likeSDSq += self.dSq(posterPost.likes,avgLikes)
						#print posterPost.reacts
						totalReacts = reduce(lambda y,z:y+z, map(lambda a: posterPost.reacts[a], posterPost.reacts.keys()))
						tReactsSDSq += self.dSq(totalReacts,avgTotalReacts)
						for i in range(len(iReactsSDSq)):
							iReactsSDSq[i] += self.dSq(posterPost.reacts[posterPost.reacts.keys()[i]],avgIndivReacts[i])

					likeVariance = float(likeSDSq)/num
					tReactsVariance = float(tReactsSDSq)/num
					iReactsVariance = [float(iReactsSDSq[x])/num for x in range(len(iReactsSDSq))]
					zScores = [likeVariance**0.5,tReactsVariance**0.5,[iReactsVariance[x]**0.5 for x in range(len(iReactsVariance))]]
				else:
					return None
			else:
				num = len(self.allPosts)-1
				if num > 0:
					avgLikes = 0
					avgTotalReacts = 0
					avgIndivReacts = [0 for x in range(len(post.reacts))]
					for allPost in self.allPosts:
						avgLikes += allPost.likes
						avgTotalReacts += reduce(lambda y,z:y+z, map(lambda a: allPost.reacts[a], allPost.reacts.keys()))
						for i in range(len(allPost.reacts)):
							avgIndivReacts[i] += allPost.reacts[allPost.reacts.keys()[i]]

					#~	[ ] make this more efficient by saving avgLikes (which is really a sum up until this point) and calculating the average
					#		separately, since that value can be updated everytime a new post is added
					avgLikes = float(avgLikes)/num
					avgTotalReacts = float(avgTotalReacts)/num
					avgIndivReacts = [float(avgIndivReacts[x])/num for x in range(len(avgIndivReacts))]

					# print 'avg: ',[avgLikes,avgTotalReacts,avgIndivReacts]

					likeSDSq = 0	#likes sum of differences squared
					tReactsSDSq = 0
					iReactsSDSq = [0 for i in range(len(post.reacts))]
					for allPost in self.allPosts:
						likeSDSq += self.dSq(allPost.likes,avgLikes)
						totalReacts = reduce(lambda y,z:y+z, map(lambda a: allPost.reacts[a], allPost.reacts.keys()))
						tReactsSDSq += self.dSq(totalReacts,avgTotalReacts)
						for i in range(len(iReactsSDSq)):
							iReactsSDSq[i] += self.dSq(allPost.reacts[allPost.reacts.keys()[i]],avgIndivReacts[i])
				
					likeVariance = float(likeSDSq)/num
					tReactsVariance = float(tReactsSDSq)/num
					iReactsVariance = [float(iReactsSDSq[x])/num for x in range(len(iReactsSDSq))]
					zScores = [likeVariance**0.5,tReactsVariance**0.5,[iReactsVariance[x]**0.5 for x in range(len(iReactsVariance))]]
				else:
					return None
			#debug print that shows the calculated zScores
			print 'z: ',zScores
			return [float(likes-avgLikes)/zScores[0] if zScores[0]!=0 else 0,
				float(tReacts-avgTotalReacts)/zScores[1] if zScores[1]!=0 else 0,
				[(float(iReacts[x]-avgIndivReacts[x])/zScores[2][x] if zScores[2][x]!=0 else 0) for x in range(len(iReacts))]]

	def standardDevPoster(self,poster):
		#~	[ ] current unimplemented

		#calculates the standard deviation of a ContentProvider compared against all others

		if poster not in self.posters:
			print 'what you doin\' yo'
		else:
			allPosts = self.posters[poster].posts

	def setAdjustment(self,adjustment):
		self.adjustment = adjustment

	def getLambda(self, i):
		#returns lambda functions that calculate a variety of statistics for a individual poster

		def filtered(x):
			return filter(lambda a:a.likes>=self.adjustment,self.posters[x].posts)

		def filteredLikes(x):
			adjPosts = filtered(x)
			if len(adjPosts)>0:
				return reduce(lambda x,y: x+y, map(lambda z: z.likes,adjPosts))
			else:
				return 0

		def filteredPosts(x):
			adjPosts = filtered(x)
			if len(adjPosts)>0:
				return len(adjPosts)
			else:
				return 1

		paramDict = {
			0:lambda x:	#likes
				self.posters[x].totalLikes if self.adjustment==0
				else filteredLikes(x),
			1:lambda x:	#likes_avg
				float(paramDict[0](x))/paramDict[2](x),
			2:lambda x:	#posts
				self.posters[x].totalPosts if self.adjustment==0
				else filteredPosts(x),
			3:lambda x:	#reacts
				reduce(lambda y,z:y+z, map(lambda a: self.posters[x].totalReacts[a], self.posters[x].totalReacts)),
			4:lambda x:	#reacts_avg
				float(paramDict[3](x))/paramDict[2](x),
			5:lambda x:	#love
				self.posters[x].totalReacts['Love'],
			6:lambda x:	#love_avg
				float(paramDict[5](x))/paramDict[2](x),
			7:lambda x:	#haha
				self.posters[x].totalReacts['Haha'],
			8:lambda x:	#haha_avg
				float(paramDict[7](x))/paramDict[2](x),
			9:lambda x:	#wow
				self.posters[x].totalReacts['Wow'],
			10:lambda x:	#wow_avg
				float(paramDict[9](x))/paramDict[2](x),
			11:lambda x:	#sad
				self.posters[x].totalReacts['Sad'],
			12:lambda x:	#sad_avg
				float(paramDict[11](x))/paramDict[2](x),
			13:lambda x:	#pride
				self.posters[x].totalReacts['Pride'],
			14:lambda x:	#pride_avg
				float(paramDict[13](x))/paramDict[2](x),
			15:lambda x:	#angry
				self.posters[x].totalReacts['Angry'],
			16:lambda x:	#angry_avg
				float(paramDict[15](x))/paramDict[2](x),
			17:lambda x:	#thankful
				self.posters[x].totalReacts['Thankful'],
			18:lambda x:	#thankful_avg
				float(paramDict[17](x))/paramDict[2](x),
			19:lambda x:	#pure_likes
				self.posters[x].totalReacts['Like'],
			20:lambda x:	#pure_likes_avg
				float(paramDict[19](x))/paramDict[2](x),
			21:lambda x:	#mod
			self.posters[x].mod,
			22:lambda x:	#name
				x
		}
		return paramDict[i]

	def sort(self,*args):
		#establishes an order to sort things in by taking in a list of arguments that indicate which
		#	values should be summed before comparison - the resulting sorted order is saved in
		#	self.sortedKeys and the parameters in self.params, to be accessed in other methods that involve sorting

		## params of ContentProviders
		# self.name = ''
		# self.posts = []
		# self.mod = 0
		# self.totalLikes = 0
		# self.totalReacts = {"Haha":0,"Like":0,"Love":0,"Wow":0,"Sad":0,"Pride":0,"Angry":0}
		# self.totalPosts = 0

		paramWordDict = {
			'likes':0,
			'likes_avg':1,
			'posts':2,
			'reacts':3,
			'reacts_avg':4,
			'love':5,
			'love_avg':6,
			'haha':7,
			'haha_avg':8,
			'wow':9,
			'wow_avg':10,
			'sad':11,
			'sad_avg':12,
			'pride':13,
			'pride_avg':14,
			'angry':15,
			'angry_avg':16,
			'thankful':17,
			'thankful':18,
			'pure_likes':19,
			'pure_likes_avg':20,
			'mod':21,
			'poster':22
		}
		reverseWordDict = {}
		for key in paramWordDict.keys():
			reverseWordDict[paramWordDict[key]]=key

		keys = self.posters.keys()
		# print keys
		params = []
		#checking how args handles lists
		#it just gives a list
		#print args
		arg_output = 'args:'
		for arg in args:
			if type(arg) is int:
				arg_output+=' '+reverseWordDict[arg]
				params += [self.getLambda(arg)]
			elif type(arg) is list:
				for argArgs in arg:
					if type(argArgs) is int:
						arg_output+=' '+reverseWordDict[argArgs]
						params += [self.getLambda(argArgs)]
					elif argArgs in paramWordDict:
						arg_output+=' '+paramWordDict[argArgs]
						params+= [self.getLambda(paramWordDict[argArgs])]
			elif arg in paramWordDict:
				arg_output+=' '+paramWordDict[arg]
				params+= [self.getLambda(paramWordDict[arg])]
			else:
				print 'invalid arg: %s'%arg

		if len(args)==0:
			print arg_output+' None'
		else:
			print arg_output

		self.params = params
		#testing all the lambdas
		# jakob = 'Jakob Myers'
		# print getLambda(3)(jakob)
		# print map_reduce(jakob)

		if (21 in params) ^ (22 in params) and len(params)>1:
			print 'these params don\'t really make sense but w\\e'

		if len(params)==0:
			self.sortedKeys = sorted(keys,cmp = lambda x,y:cmp(self.getLambda(0)(y),self.getLambda(0)(x)))
			# print self.sortedKeys
		else:
			self.sortedKeys = sorted(keys,cmp = lambda x,y:cmp(self.map_reduce(y),self.map_reduce(x)))
			# print self.sortedKeys
		#print 'sorted keys: '+str(self.sortedKeys)

	def printSummary(self,sort=False):
		#prints out a summary of all the posters, which currently is a very barebones single value that
		#	defaults to highest total likes but otherwise is based on the sorting params

		#~	the sort=True parameter doesn't do what I really want it to yet, since sorting it actually
		#		undoes previously performed sorting by defaulting to sorting in order of avgLikes
		# 	probably should add in another param 'params' that feeds straight into sort(), but probably
		#		want to force explicit use of that param with fparam or w/e
		#	[ ] resolved

		keys = self.posters.keys()
		if sort:
			self.sort()
		for key in self.sortedKeys:
			if len(self.params)>0:
				print key+':\t'+('\t' if len(key)<7 else '')+('\t' if len(key)<15 else '')+('\t' if len(key)<23 else '')+str(self.map_reduce(key))[:5]
			else:
				print key+':\t'+('\t' if len(key)<7 else '')+('\t' if len(key)<15 else '')+('\t' if len(key)<23 else '')+str(self.getLambda(0)(key))[:5]


class myHTMLParser(HTMLParser):
	#~	[ ] create an actual __init__ method

	#performs HTML parsing work on very specific sections of HTML code that has been obtained from the Facebook page of a group
	#	and stores it in a list of Posts that is later fed into the analysis.addPosts() method when it is called in the
	#	analysis.run() method

	#~unknown behavior when the entirety of a page's HTML is fed in - currently only tested on code that includes just the
	#	feed, and has only been tested on a single group's page. Could potentially have unpredicted behavior when run on 
	#	the HTML of a different group
	#	[X] run on the HTML of a different group
	#	[X] run on the complete HTML of the group
	#	[ ] run on the complete HTML of a different group

	attrCount = {}
	dataList = []
	currentPost = Post()
	postList = []
	tag = 'post'

	def handle_starttag(self, tag, attrs):
		#sets self.tag based on the attrs attached to a given tag, which allow the handle_data() method to know what
		#	type of data to expect
		#there are also some data types that are assigned in this method outright due to their information being stored
		#	in the attrs, like reacts and time
		
		#these dicts contain empirically obtained attributes that have been strongly correlated with the identity
		#	of the next datum to be parsed after a given tag, or of data contained within the attrs themselves
		postAttr = ('class','_4-u2 mbm _4mrt _5jmm _5pat _5v3q _4-u8')
		attrDict = {
			('class','_1g5v'):"total likes",
			('data-ft','{"tn":";"}'):"poster", #text post
			('class','_1mto'):"comment",
			('class','_3b-9'):"comment",
			('data-ft','{"tn":"K"}'):"text",
			('data-ft','{"tn":"l"}'):"poster", #shared post
		}
		reactsOnly = ('class','_3emk')
		timeStamp = {
			('class','_5ptz'):1,
			('class','_5ptz timestamp livetimestamp'):2
		}
		postType = {
			#('class','fwb'):"name change",
			#('data-ft','{"tn":"C"}'):"name box",
			('data-ft','{"tn":"E"}'):"photo",
			('class','_53j5'):"live",
			#('data-ft','{"tn":"F"}'):"live2"
		}
		modMeLol = ('class','_4bo_ _3bhy')

		reactionTag = False
		timeTag = 0
		for attr in attrs:
			if attr in self.attrCount:
				self.attrCount[attr]+=1
			else:
				self.attrCount[attr]=1
			if attr == postAttr:
				#print self.currentPost
				if not self.currentPost.isNull():
					self.postList += [self.currentPost]
					self.currentPost = Post()
					if self.currentPost.type!=[]:
						print 'wat'
				self.tag = 'post'
			elif attr in attrDict:
				if self.tag != 'comment':
					self.tag = attrDict[attr]
			elif attr == reactsOnly:
				reactionTag = True
			elif attr in timeStamp and self.currentPost.datetimeNull():
				timeTag = timeStamp[attr]
			if attr in postType:
				#print attr
				self.currentPost.setType(postType[attr])

		if reactionTag:
			aria = filter(lambda x: x[0]=='aria-label',attrs)[0][1]
			num,react = aria.split(' ')
			self.tag = react.lower()
			self.currentPost.setReacts(react,num)
			#print aria
		if timeTag > 0:
			if self.tag != 'comment':
				if timeTag == 1:
					humantime = attrs[0][1]
					utc = attrs[1][1]
					self.currentPost.setDatetime(humantime)
					self.currentPost.setUTC(utc)
				elif timeTag == 2:
					humantime = attrs[0][1]
					utc = filter(lambda x: x[0]=='data-utime',attrs)[0][1]
					# print humantime
					# print utc
					self.currentPost.setDatetime(humantime)
					self.currentPost.setUTC(utc)
					#print self.currentPost.datetime


	# def handle_endtag(self, tag):
	# 	print "end\t:", tag

	def handle_data(self, data):
		#accesses the self.tag set in handle_starttag() to determine what to do with the data

		#print (self.tag, data)
		if self.tag != 'comment':
			if self.tag == 'poster':
				if self.currentPost.posterNull():
					self.currentPost.setPoster(data)
				elif 'changed the name of the group' in data:
					self.currentPost.setText(data[1:])
					self.currentPost.setType('name change')
			elif self.tag == 'total likes' and self.currentPost.likesNull():
				self.currentPost.setLikes(int(data))
			elif self.tag == 'text':
				self.currentPost.setType('text')
				self.currentPost.setText(data)
			elif self.tag == 'datetime':
				self.currentPost.setDatetime(data)
			elif self.tag == 'admin':
				self.currentPost.setType('admin')
			self.dataList+=[(self.tag,data)]

	def printAttrFrequency(self):
		attrList = self.attrCount.keys()
		attrList.sort(cmp = lambda x,y:cmp(self.attrCount[x],self.attrCount[y]))
		for attr in attrList:
			print attr,': ',self.attrCount[attr]

	def printData(self):
		for i in self.dataList:
			print i

	def printPosts(self, concise=False):
		#prints out all the posts that have been parsed, with the concise param indicating that
		#	only some information is needed

		#print 'printPosts called'
		if concise:
			for post in self.postList:
				print 'Poster:\t',post.poster
				# print 'Date time:\t%s (%s)'%(post.datetime,post.UTC)
				# print 'Likes:\t',post.likes
				print 'Post type:\t',post.type
		else:
			for post in self.postList:
				print post

#main method: this is where the magic happens

#print range(6,20,2)

fileName = 'epoch2.txt'
analysis = pageAnalysis()
analysis.run(fileName)
print len(analysis.allPosts)
analysis.sort(1)
analysis.printSummary()
analysis.setAdjustment(10)
analysis.sort(1)
analysis.printSummary()
# mostRecentPost = analysis.allPosts[0]
# print analysis.standardDevPost(mostRecentPost)
# print mostRecentPost
# for recentPost in analysis.allPosts[1:10]:
# 	print analysis.standardDevPost(recentPost,False)
# 	print analysis.standardDevPost(recentPost)
# 	print recentPost
# analysis.sort(4)
#for post in analysis.allPosts:
	#print post