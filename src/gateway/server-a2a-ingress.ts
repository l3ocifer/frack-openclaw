/**
 * Native A2A JSON-RPC ingress.
 *
 * Homelab-local (see homelab/PATCHES.md, patch id `a2a-gateway-ingress`).
 * Serves `/.well-known/agent-card.json`, `/a2a` and `/a2a/v1/*` so the
 * agent-bus and cross-agent handoffs reach this agent natively instead of
 * through a sidecar. Inbound A2A is bridged onto the same embedded agent
 * runtime as the WebSocket `chat.send` path.
 *
 * This lives in its own module rather than inline in the gateway startup
 * path: it previously sat in `server.impl.ts` and was silently dropped by an
 * upstream sync once already (last present in cc0065d3b2), which 404'd every
 * inbound `POST /a2a/v1/message:send` and meant missions never reached a
 * turn. Upstream then split `server.impl.ts` into `server-start.ts` plus the
 * `server-startup-*` modules, so keeping the implementation here reduces the
 * patch to a single wiring line in `server-runtime-state-prepare.ts`.
 */
import type { IncomingMessage, ServerResponse } from "node:http";
import type { GatewayRequestHandlers } from "./server-methods/shared-types.js";
import type { GatewayRequestContext } from "./server-methods/types.js";

type A2aRequestBody = Record<string, unknown>;

async function readA2aJsonBody(req: IncomingMessage): Promise<A2aRequestBody> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk as Uint8Array));
  }
  if (chunks.length === 0) {
    return {};
  }
  const raw = Buffer.concat(chunks).toString("utf8");
  return raw.trim() ? (JSON.parse(raw) as A2aRequestBody) : {};
}

function writeA2aJson(res: ServerResponse, statusCode: number, body: unknown): void {
  const payload = Buffer.from(JSON.stringify(body));
  res.statusCode = statusCode;
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Content-Length", String(payload.length));
  res.end(payload);
}

function a2aParams(body: A2aRequestBody): A2aRequestBody {
  return body.params && typeof body.params === "object" && !Array.isArray(body.params)
    ? (body.params as A2aRequestBody)
    : body;
}

function a2aText(body: A2aRequestBody): string {
  const params = a2aParams(body);
  const message =
    params.message && typeof params.message === "object" && !Array.isArray(params.message)
      ? (params.message as A2aRequestBody)
      : params;
  const parts = Array.isArray(message.parts) ? message.parts : [];
  const chunks = parts
    .filter((part): part is A2aRequestBody => typeof part === "object" && part !== null)
    .map((part) => (typeof part.text === "string" ? part.text : ""))
    .filter(Boolean);
  if (chunks.length > 0) {
    return chunks.join("\n\n");
  }
  for (const key of ["text", "goal"]) {
    const value = params[key] ?? body[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }
  return JSON.stringify(body);
}

function a2aTaskId(body: A2aRequestBody): string {
  const params = a2aParams(body);
  for (const key of ["task_id", "taskId", "id"]) {
    const value = params[key] ?? body[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
  }
  return `a2a-${Date.now().toString(36)}`;
}

function a2aJsonRpcResult(id: unknown, result: unknown): A2aRequestBody {
  return { jsonrpc: "2.0", id: id ?? null, result };
}

/**
 * Builds the A2A ingress handler. Returns `true` when the request was handled
 * so the caller can fall through to normal gateway routing otherwise.
 *
 * `getGatewayRequestContext` is read per request, not captured: the context is
 * only populated once startup finishes, and this handler is constructed while
 * runtime state is still being assembled.
 */
export function createA2aIngressHandler(params: {
  getGatewayRequestContext: () => GatewayRequestContext | undefined;
}): (req: IncomingMessage, res: ServerResponse) => Promise<boolean> {
  return async (req, res) => {
    const url = new URL(req.url ?? "/", "http://localhost");
    if (req.method === "GET" && url.pathname.startsWith("/.well-known/")) {
      const agentId = process.env.AGENT_ID?.trim() || "main";
      writeA2aJson(res, 200, {
        name: agentId,
        description: `${agentId} OpenClaw native A2A endpoint`,
        url: `http://${agentId}.agents-shared.svc.cluster.local:8443`,
        version: "1.0.0",
        protocolVersion: "0.3.0",
        preferredTransport: "JSONRPC",
        capabilities: {
          streaming: false,
          pushNotifications: false,
          stateTransitionHistory: false,
        },
        defaultInputModes: ["text/plain", "application/json"],
        defaultOutputModes: ["application/json"],
        skills: [
          {
            id: "message-send",
            name: "message/send",
            description: "Send an A2A handoff into the native OpenClaw agent runtime.",
          },
        ],
      });
      return true;
    }
    if (req.method !== "POST") {
      writeA2aJson(res, 405, { error: "method not allowed" });
      return true;
    }
    const body = await readA2aJsonBody(req);
    const taskId = a2aTaskId(body);
    if (url.pathname === "/a2a/v1/tasks/get") {
      writeA2aJson(
        res,
        200,
        a2aJsonRpcResult(body.id, { id: taskId, status: { state: "submitted" } }),
      );
      return true;
    }
    const gatewayRequestContext = params.getGatewayRequestContext();
    if (!gatewayRequestContext) {
      writeA2aJson(
        res,
        503,
        a2aJsonRpcResult(body.id, {
          id: taskId,
          status: { state: "failed" },
          details: "gateway still starting",
        }),
      );
      return true;
    }
    const message = a2aText(body);
    // Per-task session key: each mission/handoff gets its own transcript +
    // session-write-lock lane, so inbound A2A turns never serialize behind a
    // single shared `agent:main:a2a:a2a` session (the documented re-entrant
    // lock self-deadlock). Re-dispatch of the same task_id resumes the same
    // session, preserving turn continuity.
    const sessionKey = `agent:main:a2a:${taskId}`;
    let accepted = false;
    let resultPayload: unknown;
    let resultError: unknown;
    const { chatHandlers } = await import("./server-methods/chat.js");
    const chatSendHandler = chatHandlers["chat.send"];
    if (!chatSendHandler) {
      writeA2aJson(
        res,
        500,
        a2aJsonRpcResult(body.id, {
          id: taskId,
          status: { state: "failed" },
          details: "chat.send handler unavailable",
        }),
      );
      return true;
    }
    await chatSendHandler({
      req: { type: "req", id: `a2a-${taskId}`, method: "chat.send" },
      client: null,
      isWebchatConnect: () => false,
      context: gatewayRequestContext,
      params: { sessionKey, message, idempotencyKey: taskId },
      respond: (ok: boolean, payload?: unknown, error?: unknown) => {
        accepted = ok === true;
        resultPayload = payload;
        resultError = error;
      },
    } as Parameters<GatewayRequestHandlers[string]>[0]);
    writeA2aJson(
      res,
      accepted ? 202 : 500,
      a2aJsonRpcResult(body.id, {
        id: taskId,
        status: { state: accepted ? "submitted" : "failed" },
        details: accepted ? resultPayload : resultError,
      }),
    );
    return true;
  };
}
