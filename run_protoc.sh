#!/bin/bash
set -x # Echo on
python3.10 -m grpc_tools.protoc --proto_path=./vit_worker_client/config --python_out=./vit_worker_client/config --grpc_python_out=./vit_worker_client/config ./vit_worker_client/config/image_classification.proto
