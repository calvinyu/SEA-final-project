import mapreduce.framework as framework
import classification.trainer as trainer
import tornado.ioloop

'''
mrf = framework.MapReduceFramework()
mrf.getWorkerInfo('address.json')
mrf.mapReduce('invertedIndex/ii_jobs', 'invertedIndex.IImapper', 4, 'invertedIndex.IIreducer', 'constants/invertedIndex')
tornado.ioloop.IOLoop.instance().start()

'''

'''
mrf = framework.MapReduceFramework()
mrf.getWorkerInfo('address.json')
mrf.mapReduce('constants/input', 'src.movieIndexer.mapper', 4, 'src.movieIndexer.reducer', 'constants/output')
tornado.ioloop.IOLoop.instance().start()
'''

worker_address = 'classification/address.json'
raw_data = 'constants/Genre_dict'
training_set = 'constants/training_set.p'
weights_dir = 'constants/classification_weights'
tn = trainer.Trainer()
tn.setWorkerInfo(worker_address)
genres = tn.processRawData(raw_data, training_set)
tn.setTraningParameter(0.9, 200, 0.01)
tn.train(training_set, genres, weights_dir)
tornado.ioloop.IOLoop.instance().start()
tn.generateWeightTable(weights_dir)
