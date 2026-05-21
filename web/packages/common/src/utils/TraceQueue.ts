// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// OpenTelemetry attribute values can be strings, numbers, booleans, arrays of these types, or undefined
type SparseArray<T> = Array<null | undefined | T>;
type AttributeValue =
  | null
  | undefined
  | string
  | number
  | boolean
  | SparseArray<string>
  | SparseArray<number>
  | SparseArray<boolean>;

export interface TraceSpan {
  traceId: string;
  spanId: string;
  parentSpanId?: string;
  operationName: string;
  startTime: number;
  endTime?: number;
  duration?: number;
  tags?: Record<string, AttributeValue>;
  logs?: Array<{
    timestamp: number;
    fields: Record<string, AttributeValue>;
  }>;
  status?: {
    code: number;
    message?: string;
  };
}

export interface TraceData {
  id: string;
  traceId: string;
  timestamp: number;
  severity: 'error' | 'warning' | 'info' | 'debug';
  message: string;
  context?: {
    url?: string;
    method?: string;
    statusCode?: number;
    userId?: string;
    sessionId?: string;
    service?: string;
    version?: string;
  };
  spans: TraceSpan[];
  error?: {
    name: string;
    message: string;
    stack?: string;
  };
  metadata?: Record<string, AttributeValue>;
}

export type TraceQueueEvent =
  | { type: 'added'; trace: TraceData }
  | { type: 'removed'; trace: TraceData }
  | { type: 'cleared'; traces: TraceData[] }
  | { type: 'changed'; traces: TraceData[] };

export type TraceQueueListener = (event: TraceQueueEvent) => void;

const minute = 60 * 1000;
const PURGE_INTERVAL_MS = 500;
const MAX_TRACES = 100;
const DEFAULT_TIMEOUT_MS = 5 * minute;

export class TraceQueue {
  private static instance: TraceQueue | undefined;
  private traces: TraceData[] = [];
  private listeners: Set<TraceQueueListener> = new Set();
  private readonly maxSize: number;
  private readonly defaultTimeoutMs: number;
  private expiryMap: Map<string, number> = new Map();
  // node uses `Timeout` instead of `number` as the return-type for setInterval
  // as such it is **technically** incorrect to use `number` here & TS was whining about it
  private purgeInterval: ReturnType<typeof setInterval> | null = null;

  private constructor() {
    this.maxSize = MAX_TRACES;
    this.defaultTimeoutMs = DEFAULT_TIMEOUT_MS;
  }

  public static getInstance(): TraceQueue {
    if (!TraceQueue.instance) {
      TraceQueue.instance = new TraceQueue();
    }
    return TraceQueue.instance;
  }

  public static resetInstance(): void {
    if (TraceQueue.instance) {
      TraceQueue.instance.destroy();
      TraceQueue.instance = undefined;
    }
  }

  public addTrace(trace: TraceData): void {
    const expiryTime = Date.now() + this.defaultTimeoutMs;

    const existingIndex = this.traces.findIndex((t) => t.id === trace.id);
    if (existingIndex !== -1) {
      // Merge spans and update trace metadata
      const existingTrace = this.traces[existingIndex];
      const mergedTrace = this.mergeTraces(existingTrace, trace);
      this.traces[existingIndex] = mergedTrace;
      this.expiryMap.set(trace.id, expiryTime);
    } else {
      this.traces.unshift(trace);
      this.expiryMap.set(trace.id, expiryTime);

      if (this.traces.length > this.maxSize) {
        const removedTraces = this.traces.splice(this.maxSize);
        removedTraces.forEach((removedTrace) => {
          this.expiryMap.delete(removedTrace.id);
        });
      }
    }

    this.traces.sort((a, b) => b.timestamp - a.timestamp);
    this.managePurgeInterval();
    this.emitEvent('added', trace);
    this.emitEvent('changed');
  }

  /**
   * Adds a span to an existing trace or creates a new trace if one doesn't exist.
   * This is the preferred method for adding spans from OpenTelemetry instrumentation.
   */
  public addSpan(span: TraceSpan): void {
    const existingTrace = this.traces.find((t) => t.traceId === span.traceId);

    if (existingTrace) {
      // Check if span already exists (avoid duplicates)
      const spanExists = existingTrace.spans.some((s) => s.spanId === span.spanId);
      if (!spanExists) {
        existingTrace.spans.push(span);
        this.updateTraceMetadataFromSpans(existingTrace);

        // Update expiry time
        const expiryTime = Date.now() + this.defaultTimeoutMs;
        this.expiryMap.set(existingTrace.id, expiryTime);

        this.traces.sort((a, b) => b.timestamp - a.timestamp);
        this.managePurgeInterval();
        this.emitEvent('added', existingTrace);
        this.emitEvent('changed');
      }
    } else {
      // Create new trace from span
      const newTrace: TraceData = {
        id: span.traceId,
        traceId: span.traceId,
        timestamp: span.startTime,
        severity: this.getSeverityFromSpan(span),
        message: span.operationName,
        spans: [span],
        context: this.extractContextFromSpan(span),
      };

      this.addTrace(newTrace);
    }
  }

  public removeTrace(traceId: string): boolean {
    const index = this.traces.findIndex((t) => t.id === traceId);
    if (index !== -1) {
      const removedTrace = this.traces.splice(index, 1)[0];
      this.expiryMap.delete(traceId);
      this.managePurgeInterval();
      this.emitEvent('removed', removedTrace);
      this.emitEvent('changed');
      return true;
    }
    return false;
  }

  public getTraces(): readonly TraceData[] {
    return [...this.traces];
  }

  public getTrace(traceId: string): TraceData | undefined {
    return this.traces.find((t) => t.id === traceId);
  }

  public clearTraces(): void {
    const clearedTraces = [...this.traces];
    this.traces = [];
    this.expiryMap.clear();
    this.stopPurgeInterval();
    this.emitEvent('cleared', clearedTraces);
    this.emitEvent('changed');
  }

  public getSize(): number {
    return this.traces.length;
  }

  public subscribe(listener: TraceQueueListener): () => void {
    this.listeners.add(listener);
    return () => {
      this.listeners.delete(listener);
    };
  }

  public unsubscribe(listener: TraceQueueListener): void {
    this.listeners.delete(listener);
  }

  public getSubscriberCount(): number {
    return this.listeners.size;
  }

  public filterTraces(filter: {
    severity?: TraceData['severity'];
    timeRange?: { start: number; end: number };
    searchText?: string;
    service?: string;
    excludeExpired?: boolean;
  }): TraceData[] {
    return this.traces.filter((trace) => {
      if (filter.excludeExpired && this.isTraceExpired(trace)) {
        return false;
      }

      if (filter.severity && trace.severity !== filter.severity) {
        return false;
      }

      if (filter.timeRange) {
        if (trace.timestamp < filter.timeRange.start || trace.timestamp > filter.timeRange.end) {
          return false;
        }
      }

      if (filter.searchText) {
        const searchLower = filter.searchText.toLowerCase();
        const messageMatch = trace.message.toLowerCase().includes(searchLower);
        const errorMatch = trace.error?.message?.toLowerCase().includes(searchLower);
        const spanMatch = trace.spans.some((span) =>
          span.operationName.toLowerCase().includes(searchLower)
        );

        if (!messageMatch && !errorMatch && !spanMatch) {
          return false;
        }
      }

      if (filter.service && trace.context?.service !== filter.service) {
        return false;
      }

      return true;
    });
  }

  public cleanup(): void {
    if (this.listeners.size > 0) {
      return;
    }
    this.purgeExpiredTraces();
  }

  public destroy(): void {
    this.stopPurgeInterval();
    this.traces = [];
    this.expiryMap.clear();
    this.listeners.clear();
    TraceQueue.instance = new TraceQueue();
  }

  private isTraceExpired(trace: TraceData, now: number = Date.now()): boolean {
    const expiryTime = this.expiryMap.get(trace.id);
    return expiryTime ? now >= expiryTime : false;
  }

  private purgeExpiredTraces(): void {
    if (this.listeners.size > 0) {
      return;
    }

    const now = Date.now();
    const expiredTraces: TraceData[] = [];

    this.traces.forEach((trace) => {
      if (this.isTraceExpired(trace, now)) {
        expiredTraces.push(trace);
      }
    });

    if (expiredTraces.length > 0) {
      expiredTraces.forEach((trace) => {
        const index = this.traces.findIndex((t) => t.id === trace.id);
        if (index !== -1) {
          this.traces.splice(index, 1);
          this.expiryMap.delete(trace.id);
          this.emitEvent('removed', trace);
        }
      });
      this.emitEvent('changed');
    }

    this.managePurgeInterval();
  }

  private managePurgeInterval(): void {
    const hasTraces = this.traces.length > 0;

    if (hasTraces && !this.purgeInterval) {
      this.purgeInterval = setInterval(() => {
        this.purgeExpiredTraces();
      }, PURGE_INTERVAL_MS);
    } else if (!hasTraces && this.purgeInterval) {
      this.stopPurgeInterval();
    }
  }

  private stopPurgeInterval(): void {
    if (this.purgeInterval) {
      clearInterval(this.purgeInterval);
      this.purgeInterval = null;
    }
  }

  private emitEvent(type: 'added' | 'removed', trace: TraceData): void;
  private emitEvent(type: 'cleared' | 'changed', traces?: TraceData[]): void;
  private emitEvent(
    type: 'added' | 'removed' | 'cleared' | 'changed',
    data?: TraceData | TraceData[]
  ): void {
    let event: TraceQueueEvent;

    if (type === 'added' || type === 'removed') {
      event = { type, trace: data as TraceData };
    } else if (type === 'cleared') {
      event = { type, traces: (data as TraceData[]) || [] };
    } else {
      event = { type, traces: [...this.traces] };
    }

    this.listeners.forEach((listener) => {
      try {
        listener(event);
      } catch (error) {
        console.error('Error in TraceQueue listener:', error);
      }
    });
  }

  /**
   * Merges two traces, combining their spans and updating metadata.
   */
  private mergeTraces(existingTrace: TraceData, newTrace: TraceData): TraceData {
    const mergedSpans = [...existingTrace.spans];

    // Add new spans that don't already exist
    newTrace.spans.forEach((newSpan) => {
      const exists = mergedSpans.some((span) => span.spanId === newSpan.spanId);
      if (!exists) {
        mergedSpans.push(newSpan);
      }
    });

    // Merge the traces, preferring new trace's explicit values
    const mergedTrace: TraceData = {
      ...existingTrace,
      ...newTrace, // New trace values take precedence
      spans: mergedSpans,
    };

    // Only update metadata derived from spans if the new trace doesn't have explicit values
    this.updateTraceMetadataSelectively(mergedTrace, newTrace);
    return mergedTrace;
  }

  /**
   * Updates trace metadata based on spans, but only for fields not explicitly provided in the new trace.
   */
  private updateTraceMetadataSelectively(trace: TraceData, newTrace: TraceData): void {
    if (trace.spans.length === 0) return;

    // Only update timestamp if not explicitly provided in new trace
    if (newTrace.timestamp === undefined) {
      const earliestStartTime = Math.min(...trace.spans.map((s) => s.startTime));
      trace.timestamp = earliestStartTime;
    }

    // Only update severity if not explicitly provided in new trace
    if (newTrace.severity === undefined) {
      const severities = trace.spans.map((s) => this.getSeverityFromSpan(s));
      trace.severity = this.getHighestPrioritySeverity(severities);
    }

    // Only update message if not explicitly provided in new trace
    if (newTrace.message === undefined) {
      const rootSpan = trace.spans.find((s) => !s.parentSpanId);
      if (rootSpan) {
        trace.message = rootSpan.operationName;
      } else {
        const uniqueOperations = [...new Set(trace.spans.map((s) => s.operationName))];
        trace.message =
          uniqueOperations.length === 1
            ? uniqueOperations[0]
            : `${uniqueOperations.length} operations`;
      }
    }

    // Only update context if not explicitly provided in new trace
    if (newTrace.context === undefined) {
      trace.context = this.extractContextFromSpans(trace.spans);
    }
  }

  /**
   * Updates trace metadata based on all spans in the trace.
   * Used when adding new spans to an existing trace.
   */
  private updateTraceMetadataFromSpans(trace: TraceData): void {
    if (trace.spans.length === 0) return;

    // Find the earliest start time
    const earliestStartTime = Math.min(...trace.spans.map((s) => s.startTime));
    trace.timestamp = earliestStartTime;

    // Determine highest priority severity
    const severities = trace.spans.map((s) => this.getSeverityFromSpan(s));
    trace.severity = this.getHighestPrioritySeverity(severities);

    // Use root span's operation name as message, or create a summary
    const rootSpan = trace.spans.find((s) => !s.parentSpanId);
    if (rootSpan) {
      trace.message = rootSpan.operationName;
    } else {
      const uniqueOperations = [...new Set(trace.spans.map((s) => s.operationName))];
      trace.message =
        uniqueOperations.length === 1
          ? uniqueOperations[0]
          : `${uniqueOperations.length} operations`;
    }

    // Extract context from spans
    trace.context = this.extractContextFromSpans(trace.spans);
  }

  /**
   * Determines severity from a span's status.
   */
  private getSeverityFromSpan(span: TraceSpan): 'error' | 'warning' | 'info' | 'debug' {
    if (span.status?.code === 2) {
      return 'error';
    }
    // You could add more logic here based on span attributes, duration, etc.
    return 'info';
  }

  /**
   * Gets the highest priority severity from a list.
   */
  private getHighestPrioritySeverity(
    severities: ('error' | 'warning' | 'info' | 'debug')[]
  ): 'error' | 'warning' | 'info' | 'debug' {
    if (severities.includes('error')) return 'error';
    if (severities.includes('warning')) return 'warning';
    if (severities.includes('info')) return 'info';
    return 'debug';
  }

  /**
   * Extracts context from a single span.
   */
  private extractContextFromSpan(span: TraceSpan) {
    return this.extractContextFromSpans([span]);
  }

  /**
   * Extracts context from multiple spans.
   */
  private extractContextFromSpans(spans: TraceSpan[]) {
    const context: NonNullable<TraceData['context']> = {};

    spans.forEach((span) => {
      if (span.tags) {
        // Extract HTTP information
        const url = this.getStringValue(span.tags['http.url']);
        if (url) context.url = url;

        const method = this.getStringValue(span.tags['http.method']);
        if (method) context.method = method;

        const statusCode = this.getNumberValue(span.tags['http.status_code']);
        if (statusCode) context.statusCode = statusCode;

        // Extract user information
        const userId = this.getStringValue(span.tags['user.id']);
        if (userId) context.userId = userId;

        const sessionId = this.getStringValue(span.tags['session.id']);
        if (sessionId) context.sessionId = sessionId;

        // Extract service information
        const service = this.getStringValue(span.tags['service.name']);
        if (service) context.service = service;

        const version = this.getStringValue(span.tags['service.version']);
        if (version) context.version = version;
      }
    });

    return Object.keys(context).length > 0 ? context : undefined;
  }

  /**
   * Safely extracts a string value from an AttributeValue.
   */
  private getStringValue(value: AttributeValue): string | undefined {
    if (typeof value === 'string') {
      return value;
    }
    return undefined;
  }

  /**
   * Safely extracts a number value from an AttributeValue.
   */
  private getNumberValue(value: AttributeValue): number | undefined {
    if (typeof value === 'number') {
      return value;
    }
    return undefined;
  }
}
