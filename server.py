# Python std lib
import datetime
import os
import socket
import time
import sys
import contextlib
from concurrent import futures
import multiprocessing
import pickle

# 3rd party libs
import cv2
import pytesseract
import grpc
from simber import Logger
from transformers import ViTImageProcessor, ViTForImageClassification


# Local grpc module
sys.path.append("/usr/app/grpc_config")
import image_classification_pb2
import image_classification_pb2_grpc


LOG_FORMAT = "{levelname} [{filename}:{lineno}]:"
LOG_LEVEL: str = "INFO"
logger = Logger(__name__, log_path="/tmp/logs/server.log", level=LOG_LEVEL)
logger.update_format(LOG_FORMAT)

_ONE_DAY = datetime.timedelta(days=1)
NUM_WORKERS = int(os.environ.get("NUM_WORKERS", 1))


def get_text_from_image(img: bytes) -> str:
    """
    Perform image classification over an image.

    Args:
        img (bytes) : a pickled image - encoded with openCV.

    Returns:
        The text found in the image by the IMAGECLASSIFICATION module.

    """
    processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
    model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

    # By default OpenCV stores images in BGR format and since pytesseract assumes RGB format,
    # we need to convert from BGR to RGB format/mode:
    img_rgb = cv2.cvtColor(pickle.loads(img), cv2.COLOR_BGR2RGB)

    inputs = processor(images=img_rgb, return_tensors="pt")
    outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_idx = logits.argmax(-1).item()
    return model.config.id2label[predicted_class_idx]


class ImageClassificationService(image_classification_pb2_grpc.ImageClassificationService):
    @staticmethod
    def Detect(request: image_classification_pb2.ImageClassificationCandidate, context):
        return image_classification_pb2.ImageClassificationResult(text=get_text_from_image(request.image))


def _run_server(bind_address):
    logger.debug(f"Server started. Awaiting jobs...")
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=1),
        options=[
            ("grpc.max_send_message_length", -1),
            ("grpc.max_receive_message_length", -1),
            ("grpc.so_reuseport", 1),
            ("grpc.use_local_subchannel_pool", 1),
        ],
    )
    image_classification_pb2_grpc.add_ImageClassificationServiceServicer_to_server(ImageClassificationService, server)
    server.add_insecure_port(bind_address)
    server.start()
    server.wait_for_termination()


@contextlib.contextmanager
def _reserve_port():
    """Find and reserve a port for all subprocesses to use"""
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    if sock.getsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT) == 0:
        raise RuntimeError("Failed to set SO_REUSEPORT.")
    sock.bind(("", 13000))
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


def main():
    """
    Inspired from https://github.com/grpc/grpc/blob/master/examples/python/multiprocessing/server.py
    """
    logger.info(f"Initializing server with {NUM_WORKERS} workers")
    with _reserve_port() as port:
        bind_address = f"[::]:{port}"
        logger.info(f"Binding to {bind_address}")
        sys.stdout.flush()
        workers = []
        for _ in range(NUM_WORKERS):
            worker = multiprocessing.Process(target=_run_server, args=(bind_address,))
            worker.start()
            workers.append(worker)
        for worker in workers:
            worker.join()


if __name__ == "__main__":
    main()
