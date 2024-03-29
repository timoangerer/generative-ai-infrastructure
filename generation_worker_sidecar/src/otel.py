
import logging

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import \
    OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from config import get_config

config = get_config()

resource = Resource.create(
    {
        "service.name": config.otel_service_name,
    }
)


def setup_otel_tracing():
    trace.set_tracer_provider(TracerProvider(resource=resource))
    otlp_span_processor = BatchSpanProcessor(
        OTLPSpanExporter(endpoint=config.otel_exporter_otlp_endpoint)
    )
    trace.get_tracer_provider().add_span_processor(  # type: ignore
        otlp_span_processor
    )


def setup_otel_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format, datefmt=date_format)

    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    exporter = OTLPLogExporter(insecure=True, endpoint=config.otel_exporter_otlp_endpoint)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler(level=logging.NOTSET,
                             logger_provider=logger_provider)

    # Attach OTLP handler to root logger
    logging.getLogger().addHandler(handler)

    # Acticate logging instrumentation
    LoggingInstrumentor(set_logging_format=True,
                        log_level=logging.INFO).instrument()


def setup_otel():
    setup_otel_tracing()
    setup_otel_logging()
