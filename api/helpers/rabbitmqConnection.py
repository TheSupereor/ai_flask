import pika
import json

from api.services.ollama_service import generate_response

RABBITMQ_HOST = 'localhost'
MESSAGES_QUEUE_NAME = 'messages-queue'
DEAD_LETTER_QUEUE = 'dead_letter_queue'
DEFAULT_MODEL = "smollm:135m"

def process_request(request_data):
    """Processar mensagem"""
    messageInfo = request_data['data']
    response = generate_response(DEFAULT_MODEL, request_data['data']['message'])
    messageInfo['message'] = response['response'];
    return {"success": "true", "response": messageInfo}

def on_request(ch, method, props, body):
    request_data = json.loads(body.decode('utf-8'))
    print(f"Recebido: {request_data}")

    response = process_request(request_data)
    response_body = json.dumps(response)

    # Envia a resposta para a fila de retorno
    ch.basic_publish(
        exchange='',
        routing_key=props.reply_to,
        properties=pika.BasicProperties(
            correlation_id=props.correlation_id,
        ),
        body=response_body
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_rpc_server():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(
        queue=MESSAGES_QUEUE_NAME, 
        durable=True,
        arguments={
            'x-message-ttl': 60000,
            'x-dead-letter-exchange': 'dead_letter_exchange',
            'x-dead-letter-routing-key': 'dead_letter_key'
        }
    )
    #channel.exchange_declare(exchange='dead_letter_exchange', exchange_type='direct', durable=True)
    #channel.queue_declare(DEAD_LETTER_QUEUE, durable=True)
    #channel.queue_bind(DEAD_LETTER_QUEUE, exchange='dead_letter_exchange', routing_key='dead_letter_key')
    
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=MESSAGES_QUEUE_NAME, on_message_callback=on_request)
    
    print("Servidor RPC aguardando requisições...")
    channel.start_consuming()

if __name__ == "__main__":
    start_rpc_server()
