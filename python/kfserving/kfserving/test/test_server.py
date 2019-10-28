# Copyright 2019 kubeflow.org.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from tornado.httpclient import HTTPClientError
import kfserving
from typing import Dict, List


class DummyModel(kfserving.KFModel):
    def __init__(self, name):
        super().__init__(name)
        self.name = name
        self.ready = False

    def load(self):
        self.ready = True

    def predict(self, input):
        return input


class TestTFHttpServer(object):

    @pytest.fixture(scope="class")
    def app(self):  # pylint: disable=no-self-use
        model = DummyModel("TestModel")
        model.load()
        server = kfserving.KFServer()
        server.register_model(model)
        return server.create_application()

    async def test_liveness(self, http_server_client):
        resp = await http_server_client.fetch('/')
        assert resp.code == 200

    async def test_model(self, http_server_client):
        resp = await http_server_client.fetch('/v1/models/TestModel')
        assert resp.code == 200

    async def test_predict(self, http_server_client):
        resp = await http_server_client.fetch('/v1/models/TestModel:predict', method="POST",
                                              body=b'{"instances":[[1,2]]}')
        assert resp.code == 200
        assert resp.body == b'{"predictions": [[1, 2]]}'

class CustomPredictTransformer(kfserving.KFModel):
    def predict(self, input: Dict) -> Dict:
        return {"instances": [[j*2 for j in i] for i in input["instances"]]}

class TestTransformerHttpServer(object):

    @pytest.fixture(scope="class")
    def app(self):  # pylint: disable=no-self-use
        model = CustomPredictTransformer("TestModel", predictor_host='localhost')
        model.load()
        server = kfserving.KFServer()
        server.register_model(model)
        return server.create_application()

    async def test_liveness(self, http_server_client):
        resp = await http_server_client.fetch('/')
        assert resp.code == 200

    async def test_model(self, http_server_client):
        resp = await http_server_client.fetch('/v1/models/TestModel')
        assert resp.code == 200

    async def test_predict(self, http_server_client):
        resp = await http_server_client.fetch('/v1/models/TestModel:predict', method="POST",
                                              body=b'{"instances":[[1,2]]}')
        assert resp.code == 200
        assert resp.body == b'{"predictions": [[0.1, 0.9]]}'


class CustomTransformer(kfserving.KFModel):
    def predict(self, input: Dict) -> Dict:
        data = input["instances"]
        return {"instances": [[j*2 for j in i] for i in data]}

class TestTransformerWithPrePostProcessHttpServer(object):

    @pytest.fixture(scope="class")
    def app(self):  # pylint: disable=no-self-use
        model = CustomTransformer("TestModel", predictor_host='localhost')
        model.load()
        server = kfserving.KFServer()
        server.register_model(model)
        return server.create_application()

    async def test_liveness(self, http_server_client):
        resp = await http_server_client.fetch('/')
        assert resp.code == 200

    async def test_model(self, http_server_client):
        resp = await http_server_client.fetch('/v1/models/TestModel')
        assert resp.code == 200

    async def test_predict(self, http_server_client):
        resp = await http_server_client.fetch('/v1/models/TestModel:predict', method="POST",
                                              body=b'{"instances":[[1,2]]}')
        assert resp.code == 200
        assert resp.body == b'{"predictions": [[2, 4]]}'