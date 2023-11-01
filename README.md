# gRPC Vision Transformer worker

A python gRPC worker serving a **Vision Transformer** model: vit-base-patch16-224.

## What is a Vision Transformer ?

![Vision Transformer](./images/vit.gif)

The Vision Transformer, or ViT, is a model for image classification that employs a Transformer-like architecture over patches of the image. An image is split into fixed-size patches, each of them are then linearly embedded, position embeddings are added, and the resulting sequence of vectors is fed to a standard Transformer encoder. In order to perform classification, the standard approach of adding an extra learnable “classification token” to the sequence is used.

For additional ressources, please refer to [paperswithcode](https://paperswithcode.com/method/vision-transformer)

## Run the project

```bash
git clone git@github.com:rm-rfred/vit-worker.git
cd vit-worker

docker-compose build
docker-compose up -d
```

### Config files

image_classification_pb2.py and image_classification_pb2_grpc.py where generated by running :

```bash
bash run_protoc.sh
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
