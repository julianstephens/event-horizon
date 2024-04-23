import createClient, { type Middleware } from "openapi-fetch";
import type { paths } from "./api";

const throwOnError: Middleware = {
  async onResponse(res) {
    if (res.status >= 400) {
      const body = res.headers.get("content-type")?.includes("json")
        ? await res.clone().json()
        : await res.clone().text();
      throw new Error(body);
    }
    return undefined;
  },
};

const UNPROTECTED_ROUTES = ["/auth/login", "/auth/logout"];
const authMiddleware: Middleware = {
  async onRequest(req) {
    if (UNPROTECTED_ROUTES.some((pathname) => req.schemaPath == pathname)) {
      return undefined; // don’t modify request for certain paths
    }
    // fetch token, if it doesn’t exist
    const token = window.getCookie("_auth");
    if (!token) {
      throw new Error("no auth token found");
    }

    // (optional) add logic here to refresh token when it expires

    // add Authorization header to every request
    req.headers.set("Authorization", `Bearer ${token}`);
    return req;
  },
};

const client = createClient<paths>({ baseUrl: "/api" });

client.use(throwOnError);
client.use(authMiddleware);

export default client;
