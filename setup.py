from setuptools import setup

setup(
    name="vit_worker_client",
    version="1.0.0",
    author="rm-rfred",
    packages=[
        "vit_worker_client",
        "vit_worker_client.client",
        "vit_worker_client.config"
    ],
    description="ViT worker",
    install_requires=[
        "protobuf==4.24.4",
        "grpcio==1.59.0",
        "grpcio-tools==1.59.0"
    ],
)