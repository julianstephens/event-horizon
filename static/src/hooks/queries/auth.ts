import client from "@/lib/api";
import type { components } from "@/lib/api/api";

// paths
const POST_LOGIN = "/auth/login";
const POST_REGISTER = "/auth/register";
const DELETE_LOGOUT = "/auth/logout";

export const postLogin = async (
  data: components["schemas"]["LoginRequestDTO"]
) => {
  return await client.POST(POST_LOGIN, {
    body: data,
  });
};

export const postRegister = async (
  data: components["schemas"]["RegisterRequestDTO"]
) => {
  return await client.POST(POST_REGISTER, {
    body: data,
  });
};

export const deleteLogout = async () => {
  return await client.DELETE(DELETE_LOGOUT);
};
