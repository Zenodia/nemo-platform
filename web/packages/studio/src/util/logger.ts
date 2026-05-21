// SPDX-FileCopyrightText: Copyright (c) 2025-2026 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

/* eslint-disable no-console */
import { AnyValue, Logger, logs, SeverityNumber } from '@opentelemetry/api-logs';
import { OTEL_SERVICE_NAME, VERSION_SHA } from '@studio/constants/environment';

const otelLogger: Logger = logs.getLogger(OTEL_SERVICE_NAME);

/**
 * Wrapper class around the global OpenTelemetry Logger. Logs will be transported to:
 * 1. The console
 * 2. OpenTelemetry Collector (except in local and test envs - see `telemetry.ts`)
 *
 * We export a global instance of this class below (`websiteLogger`). That variable
 * should be used by individual modules, in-place of `console.log`.
 *
 * Example usage:
 *
 * ```
 * import { websiteLogger } from '@studio/util/logger';
 * websiteLogger.info('Some message to log');
 * ```
 */
class WebsiteLogger {
  private log(level: SeverityNumber, message: AnyValue) {
    if (level === SeverityNumber.ERROR) {
      console.error(message);
    } else if (level === SeverityNumber.WARN) {
      console.warn(message);
    } else if (level === SeverityNumber.INFO) {
      console.info(message);
    } else if (level === SeverityNumber.DEBUG) {
      console.debug(message);
    }
    otelLogger.emit({
      severityNumber: level,
      body: message,
    });
  }

  debug(message: AnyValue) {
    this.log(SeverityNumber.DEBUG, message);
  }

  error(message: AnyValue) {
    this.log(SeverityNumber.ERROR, message);
  }

  info(message: AnyValue) {
    this.log(SeverityNumber.INFO, message);
  }

  warn(message: AnyValue) {
    this.log(SeverityNumber.WARN, message);
  }
}

// Global instance of our logger that should be used by individual modules, in-place of `console.log`.
export const websiteLogger = new WebsiteLogger();

/**
 * Handles a generic error by logging it to the website logger.
 */
export const handleGenericError = (error: Error | string) => {
  if (error instanceof Error) {
    websiteLogger.error(JSON.stringify(error));
  } else {
    websiteLogger.error(error);
  }
};

/**
 * Logs the version of the app to the website logger.
 */
export const logVersion = async () => {
  if (VERSION_SHA) {
    websiteLogger.info(`Version: ${VERSION_SHA}`);
  }
};
