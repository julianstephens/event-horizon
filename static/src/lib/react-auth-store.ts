import createStore from "react-auth-kit/createStore";
import refreshApi from "./refresh-api";

const store = createStore({
  authName: "_auth",
  authType: "cookie",
  refresh: refreshApi,
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === "https:",
});

export default store;
