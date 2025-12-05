# API Output Object Structure Documentation

## Overview

This document describes the structure of output objects returned by the Snow Leopard API. The API uses a typed object system with different response types for various stages of query processing and result delivery.

## Core Response Types

### RetrieveResponse

The primary successful response object containing query results.

**Fields:**
- `objType`: `"retrieveResponse"`
- `callId`: Unique identifier for the API call
- `data`: List of schema data or error objects (see SchemaData and ErrorSchemaData)
- `responseStatus`: Status of the response (see ResponseStatus enum)

**Usage:** This is the main response object when a query completes successfully.

### RetrieveResponseError

Error response object when the API call fails.

**Fields:**
- `objType`: `"apiError"`
- `callId`: Unique identifier for the API call
- `responseStatus`: Status string indicating the error type
- `description`: Human-readable error description

**Usage:** Returned when the API encounters a critical error that prevents normal response processing.

## Data Objects

### SchemaData

Contains successful query results for a specific schema.

**Fields:**
- `objType`: `"schemaData"`
- `schemaId`: Identifier for the schema queried
- `schemaType`: Type of schema
- `query`: The query string executed
- `rows`: List of result rows (each row is a dictionary)
- `querySummary`: Dictionary containing query metadata and statistics
- `rowMax`: Maximum number of rows that can be returned
- `isTrimmed`: Boolean indicating if results were truncated
- `callId`: Optional call identifier

**Usage:** Each SchemaData object represents results from querying one schema. A response may contain multiple SchemaData objects if the query spans multiple schemas.

### ErrorSchemaData

Contains error information for a failed schema query.

**Fields:**
- `objType`: `"errorSchemaData"`
- `schemaType`: Type of schema that failed
- `schemaId`: Identifier for the schema
- `query`: The query string that failed
- `error`: Error message
- `querySummary`: Dictionary containing query metadata
- `datastoreExceptionInfo`: Optional additional exception details
- `callId`: Optional call identifier

**Usage:** Returned when a query against a specific schema fails. Other schemas in the same request may still succeed.

## Streaming Response Objects

The API supports streaming responses for real-time updates. The following objects are emitted during streaming:

### ResponseStart

Indicates the beginning of a streaming response.

**Fields:**
- `objType`: `"responseStart"`
- `callId`: Unique identifier for the API call
- `userQuery`: The original user query string

### ResponseData

Contains partial data during streaming.

**Fields:**
- `objType`: `"responseData"`
- `callId`: Unique identifier for the API call
- `data`: List of schema data or error objects received so far

### EarlyTermination

Indicates the response was terminated before completion.

**Fields:**
- `objType`: `"earlyTermination"`
- `callId`: Unique identifier for the API call
- `responseStatus`: Status at termination (see ResponseStatus enum)
- `reason`: Human-readable reason for termination
- `extra`: Dictionary with additional context

**Usage:** Emitted when a streaming response is cut short due to errors, token limits, or other constraints.

### ResponseLLMResult

Contains the final LLM-generated response.

**Fields:**
- `objType`: `"responseLLMResult"`
- `callId`: Unique identifier for the API call
- `responseStatus`: Final response status (see ResponseStatus enum)
- `llmResponse`: Dictionary containing the language model's response

**Usage:** The final object in a successful streaming response, containing the synthesized answer.

## Response Status Enum

The `ResponseStatus` enum indicates the outcome of an API call:

|       | VALUE                     | DESCRIPTION                            |
|-------|---------------------------|----------------------------------------|
| ✅     | `SUCCESS`                 | Query completed successfully           |
| 🤷    | `NOT_FOUND_IN_SCHEMA`     | Requested data not found in any schema |
| 🤔    | `UNKNOWN`                 | Unknown error occurred                 |
| 💥    | `INTERNAL_SERVER_ERROR`   | Server-side error                      |
| 👮‍♂️ | `AUTHORIZATION_FAILED`    | Authentication or authorization failed |
| 🤖    | `LLM_ERROR`               | Language model processing error        |
| 😩    | `LLM_TOKEN_LIMIT_REACHED` | Response exceeded token limits         |

## Type Unions

The codebase defines several type unions for working with groups of related objects:

- `RetrieveResponseObjects`: Either RetrieveResponse or RetrieveResponseError
- `ResponseDataObjects`: Any of the streaming response objects (ErrorSchemaData, ResponseStart, ResponseData, EarlyTermination, ResponseLLMResult)

## Object Identification

All objects include an `objType` field that identifies the object type. When serialized to JSON, objects use `__type__` as the discriminator field for deserialization.

## Error Handling

The API uses multiple levels of error reporting:

1. **Status codes**: Use ResponseStatus enum to indicate specific error conditions
2. **Request-level errors**: Return RetrieveResponseError for complete failures
3. **Schema-level errors**: Include ErrorSchemaData in the data list for partial failures
4. **Early termination**: Use EarlyTermination objects in streaming to signal incomplete responses

This allows handling errors gracefully and potentially use partial results even when some schemas fail.
