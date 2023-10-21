# gRPC image classification worker

A python gRPC worker serving vit-base-patch16-224 model.

## Run the project

```bash
git clone git@github.com:rm-rfred/vit-worker.git
cd vit-worker
docker-compose build
docker-compose up -d
```

## Why gRPC instead of REST ?

- Higher performances for microservice architecture
- High load APIs
- Better suited for real time / streaming apps

## gRPC architecture example

![gRPC](https://github.com/ByteByteGoHq/system-design-101/blob/main/images/grpc.jpg?raw=True)

## Dependencies

Docker version **24.0.6**, build ed223bc
Docker Compose version **v2.23.0**

### Config files

image_classification_pb2.py and image_classification_pb2_grpc.py where generated by running :

```bash
bash run_protoc.sh
```
