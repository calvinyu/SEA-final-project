import tornado.httpserver
import tornado.ioloop
import tornado.web
import hashlib
import socket
import getpass
import os, re, math, sys
import json
import pickle
import urllib
import uuid
from nltk.tokenize import RegexpTokenizer

from tornado.httpclient import AsyncHTTPClient
from tornado import gen
from tornado.options import define, options
import subprocess
from operator import mul

sys.path.append('../')
from src import color
bcolors = color.bcolors()

invertedIndex = {}

'''
recom_worker has two part: 1. movieHandler 2. reviewHandler. 
you have to init it to proper type 
e.g. 
sockets = bind_sockets(port)    
myback_movie = recom_worker.RecommApp('MovieServer', num, port)
myback_movie.app
'''

def remove_duplicates(values):
  output = []
  seen = set()
  for value in values:
    # If value has not been encountered yet,
    # ... add it to both list and set.
    if value not in seen:
      output.append(value)
      seen.add(value)
  return output

class Application(tornado.web.Application):
    def __init__(self, server):
      if (server == 'MovieServer'):
        handlers = [(r"/movie", movieHandler)]
      elif (server == 'ReviewServer'):
        handlers = [(r"/review", reviewHandler), (r"/findHistory", findHistoryHandler), (r"/update", updateHandler)]      
      else:
        raise NameError('wrong server name')
      tornado.web.Application.__init__(self, handlers)  
class updateHandler(tornado.web.RequestHandler):
  @gen.coroutine            
  def get(self):
    global invertedIndex, tokenizer
    userID = self.get_argument('user', None)
    userID = str(userID)
    print "Hi!!!%s"%userID
    movieID = self.get_argument('movieID', None)
    rating = self.get_argument('rating', None)
    if userID in invertedIndex:
      invertedIndex[userID].append((movieID, rating))
    else:
      invertedIndex[userID] = [(movieID, rating)]
    
    print "invertedIndex[userID] in updateHandler:%s"%invertedIndex[userID]
    res = {"status": "success"}
    self.write(json.dumps(res))
    


class findHistoryHandler(tornado.web.RequestHandler):
  @gen.coroutine            
  def get(self):
    global invertedIndex, tokenizer
    # print "len(invertedIndex.keys()): %s" %len(invertedIndex.keys())
    # print invertedIndex.keys()
    result = {}
    userID = self.get_argument('user', None)
    userID = str(userID)
    print userID    
    print invertedIndex[userID]
    
    try:
      result[userID] = invertedIndex[userID]
    except:
      result[userID] = []
    self.write(json.dumps(result))

class movieHandler(tornado.web.RequestHandler):
  @gen.coroutine            
  def get(self):
    global invertedIndex, tokenizer
    movieIDs = self.get_argument('movieID', None)
    MovieList = [str(t) for t in tokenizer.tokenize(movieIDs)] 
    MovieList = remove_duplicates(MovieList)
    # print "movieIDs" + str(MovieList)        
    
    result = {}
    for eachMovie in MovieList:      
      if eachMovie in invertedIndex:
        try:
          result[eachMovie].append(invertedIndex[eachMovie])
        except:
          result[eachMovie]=invertedIndex[eachMovie]
      else:
        pass
    

    self.write(json.dumps(result))



class reviewHandler(tornado.web.RequestHandler):
  @gen.coroutine            
  def get(self):
    global invertedIndex, tokenizer
    ALLcritic = self.get_argument('critics', None)        
    ALLcritic = [t.replace("_", " ") for t in tokenizer.tokenize(ALLcritic)]
    # print "ALLcritic:\n%s" % ALLcritic

    result = {}
    for eachCritic in ALLcritic:
      if eachCritic in invertedIndex:
        try:
          result[eachCritic].append(invertedIndex[eachCritic])
        except:
          result[eachCritic]=invertedIndex[eachCritic]
      else:
        pass

    self.write(json.dumps(result))




class RecommApp(object):
  def __init__(self, serverType, serverNum, port):    
    global invertedIndex, tokenizer
    if (serverType=='MovieServer'):
      pass
      path = os.path.dirname(__file__) + '/../constants/movieIndexer/' + str(serverNum) + '.out'
    elif (serverType=='ReviewServer'):
      pass
      path = os.path.dirname(__file__) + '/../constants/reviewIndexer/' + str(serverNum) + '.out'
    else:
      raise NameError('path error')    
    
    invertedIndex = pickle.load(open(path, 'r'))
    print bcolors.OKGREEN + "%s_%s\tLoading: %s\nNum of Keys:\t%s\n_____________" %(str(serverType), str(port), str(path), str(len(invertedIndex.keys()))) + bcolors.ENDC     
    tokenizer = RegexpTokenizer(r'\w+\.\_\w+|\w+\'\w+|\w+')
    self.app = tornado.httpserver.HTTPServer(Application(serverType) ) 






