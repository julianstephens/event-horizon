import createStore from "react-auth-kit/createStore";
import refreshApi from "./refresh-api";

window.getCookie = (name: string) => {
  var match = document.cookie.match(new RegExp("(^| )" + name + "=([^;]+)"));
  if (match) return match[2];
};

const store = createStore({
  authName: "_auth",
  authType: "cookie",
  refresh: refreshApi,
  cookieDomain: window.location.hostname,
  cookieSecure: window.location.protocol === "https:",
});

export default store;
