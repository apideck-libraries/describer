**Core Functionality: Bridging the Gap Between APIs and Webhooks**

The `virtualWebhook` module simulates webhook functionality for APIs that _don't_ natively support webhooks. It does this by periodically polling the third-party API, comparing the retrieved data to a previous state, and then triggering actual webhooks (managed by Apideck) when changes are detected. This allows developers to receive real-time updates from APIs that would otherwise require constant polling.

**Key Concepts:**

- **Sync Job:** The core unit of work. A `SyncJob` represents the ongoing task of monitoring a specific resource (e.g., "leads") on a specific API ("Unified API" + "Service ID") for a particular customer ("Consumer ID") within an application ("Application ID"). Each `SyncJob` tracks:

  - `applicationId`: The Apideck application ID.
  - `consumerId`: The ID of the end-customer (the user of the application).
  - `resourceId`: The specific resource being monitored (e.g., `crm.leads`).
  - `serviceId`: The third-party service (e.g., "pipedrive").
  - `unifiedApi`: The Unify API category (e.g., "crm").
  - `syncInProgress`: A boolean indicating if a sync is currently running.
  - `lastSuccessfulSync`: Information (timestamps) about the last successful data retrieval.
  - `currentSyncStartedAt`: Timestamp when the current sync run started.
  - `nextSyncAt`: Timestamp when the next scheduled sync should run.
  - `trigger`: How the sync was initiated (`manual` or `scheduled`).
  - `failedAttempts`: Counter for consecutive failed attempts.
  - `lastFailedAt`: Timestamp of the last failure.
  - `enabled`: A boolean to enable/disable the sync job.

- **Sync State:** A snapshot of the current sync process _within_ a `SyncJob`'s execution. It's passed between different parts of the execution flow. It contains the `SyncJob`, plus:

  - `encryptedApiKey`: The API key for accessing the third-party service.
  - `interval`: How often (in seconds) the resource should be checked.
  - `numberOfConsecutiveDownstreamCalls`: How many API calls can be made in a row (related to rate limiting).
  - `delay`: The delay (in seconds) between downstream API calls.
  - `detectBy`: The method for change detection ("checksum" or "timestamp").
  - `operationId`: the resource + action (e.g. `crm.leads-all`).
  - `cursor`: (Optional) A pagination cursor for APIs that support it.
  - `executionAttempt`: Number of retries of a message.
  - `lastExecution`: last time the sync was attempted.

- **Sync Message:** A message placed on a queue (SQS in this case) to trigger the execution of a sync. It contains the `SyncState`.

- **Connector:** Defines how Unify interacts with a specific third-party API. It includes information about API endpoints, authentication, and (crucially) whether virtual webhooks are supported.

- **Resource Mapping:** Defines how data from the third-party API maps to the standardized Unify data model.

- **Checksum / Timestamp:** The two primary methods for detecting changes.

  - **Checksum:** A hash of the data is stored. If the hash changes, data has changed.
  - **Timestamp:** Uses `updated_at` or similar fields to detect changes.

- **Visibility Timeout Extender:** A component to prevent messages from reappearing on the queue while they are actively being processed by extending the message visibility timeout.

- **Downstream:** Refers to the third-party API that is being polled.

**Primary Workflows:**

1.  **Setup (One-time or infrequent):**

    - **Creating Sync Jobs:** When a connection to a third-party service is established, or when virtual webhooks are enabled for an integration, `SyncJob`s are created. This happens via `createSyncJobsForConnectionUseCase` and `createSyncJobsForIntegrationUseCase`. These use cases determine which resources support virtual webhooks and create corresponding `SyncJob` entries in the database.
    - **Deleting Sync Jobs:** When a connection is removed (`deleteSyncJobsForConnectionUseCase`) or virtual webhooks are disabled for an integration (`deleteSyncJobsForIntegrationUseCase`), the corresponding `SyncJob`s are deleted.

2.  **Scheduled Sync Execution (The main loop):**

    - **`startSyncUseCase` (Scheduler):** This is the entry point for scheduled syncs. It runs periodically.

      1.  **Finds `SyncJob`s:** It queries the database for `SyncJob`s that are due to run (`getNextSyncJobs`).
      2.  **Creates `SyncState`:** For each due `SyncJob`, it creates a `SyncState` object, including retrieving the encrypted API key.
      3.  **Enqueues Messages:** It puts a `SyncMessage` (containing the `SyncState`) onto a queue for processing.

    - **`processSyncMessagesUseCase` (Queue Consumer):** This runs continuously, listening for messages on the queue.

      1.  **Dequeues Messages:** It retrieves `SyncMessage`s from the queue.
      2.  **Calls `executeSyncUseCase`:** It passes the `SyncMessage` to `executeSyncUseCase` to perform the actual sync.
      3.  **Handles Polling/Retries:** If no messages are found, it polls the queue again after a delay.

    - **`executeSyncUseCase` (The core sync logic):** This is where the bulk of the work happens.
      1.  **Validation:** Checks if the integration and connection are valid and enabled.
      2.  **Fetch Data:** Calls the third-party API (`fetchDownstreamData`) to retrieve the current data for the resource.
      3.  **Change Detection:** Compares the retrieved data to the last known state (using either checksums or timestamps).
      4.  **Trigger Webhooks:** If changes are detected, it triggers the configured webhooks (managed by Apideck).
      5.  **Update `SyncJob`:** Updates the `SyncJob` in the database with the latest status (last successful sync, next sync time, etc.).
      6.  **Pagination:** If the API uses pagination, it handles retrieving subsequent pages of data. If a cursor for the next page is present, it creates a new `SyncMessage` with the updated cursor and adds it to the queue.
      7.  **Error Handling:** Includes robust error handling, retries, and backoff logic (`handleMessageError`, `calculateBackoff`). It differentiates between transient and permanent errors.
      8.  **Visibility Timeout Management:** Uses `createVisibilityExtender` to prevent messages from reappearing on the queue while they are being actively processed.

3.  **Manual Sync Triggering:**

    - **`ScheduleVirtualWebhookSyncController` and `scheduleVirtualWebhookSyncUseCase`:** These allow for _manually_ triggering a sync for a specific resource. This is useful for immediate updates or debugging. The controller validates the request and the use case creates a `SyncJob` with the `trigger` set to `manual`. This `SyncJob` is then processed through the same `startSyncUseCase` -> `processSyncMessagesUseCase` -> `executeSyncUseCase` flow as scheduled syncs.

**Use Case Explanations and Interactions:**

1.  **`createSyncJobsForConnectionUseCase`:**

    - **Purpose:** To create `SyncJob`s when a new connection is established.
    - **How it Works:**
      1.  Gets the integration details (to check if virtual webhooks are enabled).
      2.  If enabled, it identifies the resources that support virtual webhooks.
      3.  For each supported resource, it creates a `SyncJob`, associating it with the connection's application, consumer, service, and unified API.
      4.  It stores these `SyncJob`s in the database.
    - **Interaction:** Called when a new connection is created.

2.  **`createSyncJobsForIntegrationUseCase`:**

    - **Purpose:** To create `SyncJob`s when virtual webhooks are enabled for an integration.
    - **How it Works:**
      1.  Retrieves the integration.
      2.  Checks if virtual webhooks are enabled.
      3.  Finds all connections associated with the integration and application.
      4.  For each _callable_ connection and each enabled resource, it generates a `SyncJob`.
      5.  Saves the `SyncJob`s to the database.
    - **Interaction:** Called when virtual webhooks are enabled/configured for an integration.

3.  **`deleteSyncJobsForConnectionUseCase`:**

    - **Purpose:** To remove `SyncJob`s when a connection is deleted.
    - **How it Works:** Deletes all `SyncJob`s associated with the given connection (identified by application, service, unified API, and consumer).
    - **Interaction:** Called when a connection is deleted.

4.  **`deleteSyncJobsForIntegrationUseCase`:**

    - **Purpose:** To remove `SyncJob`s when virtual webhooks are disabled for an integration, or specific resources are disabled.
    - **How it Works:**
      - If no specific resources are provided, it deletes `SyncJob`s for all resources associated with the integration.
      - If specific resources _are_ provided, it deletes `SyncJob`s only for those resources.
      - It handles deleting by integration or by individual resource, supporting multiple Unified APIs.
    - **Interaction:** Called when virtual webhooks are disabled for an integration or when specific resources are disabled.

5.  **`ScheduleVirtualWebhookSyncController` / `scheduleVirtualWebhookSyncUseCase`:**

    - **Purpose:** To allow manual triggering of a sync for a specific resource.
    - **How it Works:**
      - **Controller:** Validates the incoming request (headers, body), ensuring the necessary IDs are present.
      - **UseCase:**
        1.  Validates the connection, integration (checks if virtual webhooks are enabled), and ensures no other sync is currently in progress.
        2.  Checks to make sure that a previous sync has completed.
        3.  Creates a new `SyncJob` with the `trigger` field set to `"manual"`.
        4.  Saves the `SyncJob` to the database.
    - **Interaction:** This is triggered by an API call (likely from a developer or an internal Apideck tool). It then uses the same `startSyncUseCase` entry point as the scheduled syncs.

6.  **`startSyncUseCase`:**

    - **Purpose:** The entry point for scheduled sync execution. It finds `SyncJob`s that are ready to run and puts them on the queue.
    - **How it Works:**
      1.  Retrieves connectors that have virtual webhooks enabled.
      2.  For each connector, it finds the next `SyncJob`s that are due to run (`getNextSyncJobs`).
      3.  Creates a `SyncState` for each `SyncJob`.
      4.  Sends a `SyncMessage` (containing the `SyncState`) to the queue.
    - **Interaction:** Called periodically by a scheduler (e.g., a cron job). It's the starting point of the regular sync process.

7.  **`processSyncMessagesUseCase`:**

    - **Purpose:** The queue consumer. It retrieves messages from the queue and initiates the sync process.
    - **How it Works:**
      1.  Retrieves a `SyncMessage` from the queue.
      2.  Calls `executeSyncUseCase` to process the message.
      3.  If no messages are found, it waits (polls) for a configured period before checking again. It includes logic to retry fetching messages.
    - **Interaction:** Runs continuously, listening for messages on the queue.

8.  **`executeSyncUseCase`:**

    - **Purpose:** The core logic for performing a single sync operation. It fetches data, detects changes, triggers webhooks, and updates the `SyncJob`.
    - **How it Works:** (Detailed steps already listed above in "Primary Workflows"). This is the most complex use case, handling data retrieval, comparison, webhook triggering, pagination, and error handling.
    - **Interaction:** Called by `processSyncMessagesUseCase` for each `SyncMessage` received.

9.  **`handleMessageError`:**

    - **Purpose:** Determines whether to retry a failed `SyncMessage` or delete it from the queue
    - **How it works:**
      1. Stops the `VisibilityExtender`
      2. Checks `context.isPermanent` to determine if the error should be retried.
      3. If permanent, deletes the message from the queue.
      4. If transient, calculates backoff, retries, or deletes if max attempts reached.

10. **`calculateBackoff`:**

    - **Purpose:** Determines the delay before retrying.
    - **How it Works:** Uses a predefined `RETRY_TIMELINE` to calculate delay.

11. **`createVisibilityExtender`:**

    - **Purpose:** Creates an instance of the visibility timeout extender.
    - **How it Works:**
      - Takes configuration parameters including `messageId`, `logKey`, `heartbeatIntervalSeconds`, and `visibilityTimeoutExtensionSeconds`.
      - Provides functions to `start` and `stop` extending the message visibility.
      - Includes internal logic to handle consecutive failures and stop the heartbeat if necessary.
      - Provides a health check (`isHealthy`) to monitor the heartbeat status.
    - **Interaction:** Used by `executeSyncUseCase` to prevent messages from reappearing on the queue during processing.

**In summary:** The `virtualWebhook` module provides a robust system for simulating webhooks for APIs that don't natively support them. It uses a combination of scheduled tasks, message queues, and careful state management to ensure reliable and efficient delivery of real-time updates to users. The use cases work together in a well-defined flow, handling various scenarios like setup, scheduling, manual triggering, execution, and error handling. The detailed error handling and retry mechanisms are crucial for dealing with the inherent unreliability of external APIs. The visibility timeout extender is key for reliability in a distributed queue-based system.
