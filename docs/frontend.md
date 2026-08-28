# Frontend

The frontend uses React 19, strict TypeScript, Vite, TanStack Query, and a production Nginx build. It is deliberately an observability surface for the backend rather than a decorative chat box.

## User feedback

- Upload constraints are visible before selection.
- Accepted uploads immediately show `queued`, followed by `processing`, `ready`, or `failed`.
- Document metadata reports bytes, pages, and chunk count.
- Gemini verification reports the selected model or a safe error.
- Answers expose retrieval latency, generation latency, source count, similarity, page, and passage text.
- Empty evidence produces an explicit refusal instead of a fabricated answer.
- Tooltips explain the engineering meaning of each workflow.

## Credential handling

The Gemini key exists only in React component memory. It is not placed in local storage, session storage, cookies, URLs, analytics, or state-management caches. Refreshing the page removes it. Browser developer tools can still inspect an in-flight request, which is expected for a bring-your-own-key local demonstration.

The anonymous workspace UUID is persisted in local storage because it is an identifier, not a credential. A production deployment would replace it with authenticated server-issued identity.

