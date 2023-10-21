from concurrent import futures
import pickle

import grpc
from simber import Logger
from transformers import ViTImageProcessor, ViTForImageClassification

LOG_FORMAT = "{levelname} [{filename}:{lineno}]:"
LOG_LEVEL: str = "INFO"
logger = Logger(__name__, log_path="/tmp/logs/server.log", level=LOG_LEVEL)
logger.update_format(LOG_FORMAT)

from vit_worker_client.config import image_classification_pb2, image_classification_pb2_grpc


class ImageClassificationService(image_classification_pb2_grpc.ImageClassificationServiceServicer):
    def ApplyImageClassification(self, request):
        try:
            image = pickle.loads(request.image)
            processor = ViTImageProcessor.from_pretrained('google/vit-base-patch16-224')
            model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-224')

            inputs = processor(images=image, return_tensors="pt")
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class_idx = logits.argmax(-1).item()
            predicted_class = model.config.id2label[predicted_class_idx]
            return image_classification_pb2.ImageClassificationReply(predicted_class=predicted_class)
        except Exception as e:
            return image_classification_pb2.ImageClassificationReply(predicted_class="")

def serve():
    options = [
        ('grpc.max_send_message_length', -1),
        ('grpc.max_receive_message_length', -1),
        ('grpc.so_reuseport', 1),
        ('grpc.use_local_subchannel_pool', 1),
    ]
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=2), options=options
    )
    image_classification_pb2_grpc.add_ImageClassificationServiceServicer_to_server(ImageClassificationService(), server)
    server.add_insecure_port("[::]:13000")
    logger.info("Binding to [::]:13000")
    server.start()
    server.wait_for_termination()
    logger.info("Server stopped")

if __name__ == "__main__":
    logger.info("Staring server...")
    serve()