# [SCRUM-9] Observability: OpenTelemetry Distributed Tracing & Prometheus Metrics
import os
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.resources import Resource

def initialize_tracing(service_name):
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    
    # Send traces to OTEL Collector
    otlp_exporter = OTLPSpanExporter(
        endpoint="otel-collector:4317",
        insecure=True
    )
    
    processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)

    # Instrument Django
    DjangoInstrumentor().instrument()
    
    # Instrument Requests (outgoing calls)
    RequestsInstrumentor().instrument()
    
    # Instrument Psycopg2 (DB calls)
    Psycopg2Instrumentor().instrument()

    print(f"OpenTelemetry initialized for {service_name}")
