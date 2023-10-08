# -*- coding: utf-8 -*-
#!/usr/bin/python
import sys
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from sentence_transformers import SentenceTransformer
import torch
from itertools import islice
import json
from sentence_transformers import util
import requests
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

hostName = "0.0.0.0"

MODEL_NAME_ALL_MINILM_L6_V2 = 'all-MiniLM-L6-v2'
MODEL_NAME_ALL_MPNET_BASE_V2 = 'sentence-transformers/all-mpnet-base-v2'
model_name = MODEL_NAME_ALL_MPNET_BASE_V2

global modelPool

FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('pooled-http-server')
logger.setLevel('INFO')

modelPool = None

class ModelPool:

    models = []
    pool_size = 1

    def __init__(self, pool_size=1):
        self.pool_size = pool_size
        x = 0
        while x < pool_size:
            self.models.append(self.load_model())
            x = x + 1
        pass

    def load_model(self):
        # Load or create a SentenceTransformer model.
        model = SentenceTransformer(model_name)
        # Get device like 'cuda'/'cpu' that should be used for computation.
        if torch.cuda.is_available():
            model = model.to(torch.device("cuda"))
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            model = model.to(torch.device("mps"))
        print(model.device)
        return model

    def pop_model(self):
        while True:
            try:
                return self.models.pop()
            except IndexError:
                time.sleep(0.01)
                pass

    def return_model(self, model):
        self.models.append(model)

class MyServer(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes('{"up": true}', "utf-8"))

    def cosSim(self, text1, text2):
        start = time.time()
        model = modelPool.pop_model()
        vec1 = model.encode(text1, convert_to_tensor=True)
        vec2 = model.encode(text2, convert_to_tensor=True)
        modelPool.return_model(model)
        sim = util.pytorch_cos_sim(vec1, vec2)
        logger.info('time /cos-sim: %s', (time.time() - start))
        return sim.item()

    def dotSim(self, text1, text2):
        start = time.time()
        model = modelPool.pop_model()
        vec1 = model.encode(text1, convert_to_tensor=True)
        vec2 = model.encode(text2, convert_to_tensor=True)
        modelPool.return_model(model)
        dotsim = np.dot(vec1, vec2)
        logger.info('time /dot-sim: %s', (time.time() - start))
        return dotsim

    def vecCosSim(self, vec1, vec2):
        start = time.time()
        sim = util.pytorch_cos_sim(vec1, vec2)
        logger.info('time /vec-cos-sim: %s', (time.time() - start))
        return sim.item()

    def vecDotSim(self, vec1, vec2):
        start = time.time()
        sim = np.dot(vec1, vec2)
        logger.info('time /vec-dot-sim: %s', (time.time() - start))
        return sim

    def do_POST(self):
        global modelPool
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        content_len = int(self.headers.get('content-length', 0))
        post_body = self.rfile.read(content_len)
        input_json = json.loads(post_body) if post_body else None
        response_body = {}
        if '/vec' == self.path:
            if 'text' in input_json:
                start = time.time()
                model = modelPool.pop_model()
                vector = model.encode(input_json['text'], show_progress_bar=False)
                modelPool.return_model(model)
                response_body['text'] = input_json['text']
                response_body['vector'] = vector.tolist()
                logger.info('time /vec: %s', (time.time() - start))
        elif '/sim' == self.path:
            if 'target' in input_json and 'input' in input_json:
                response_body['sim'] = self.cosSim(input_json['target'], input_json['input']);
        elif '/vec-sim' == self.path:
            if 'target' in input_json and 'input' in input_json:
                response_body['sim'] = self.vecCosSim(input_json['target'], input_json['input'])
        self.wfile.write(json.dumps(response_body).encode('utf-8'))

if __name__ == "__main__":
    modelPool = ModelPool(int(os.environ.get('MODEL_POOL_SIZE', 8)))
    serverPort = int(os.environ.get('SERVER_PORT', '8080'))
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")