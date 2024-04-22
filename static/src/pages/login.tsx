import { postLogin } from "@/hooks/queries";
import type { User } from "@/lib/api/aliases";
import { components } from "@/lib/api/api";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [email, setEmail] = useState("spidaman@theweb.net");
  const [pwd, setPwd] = useState("********");

  const goto = useNavigate();

  const signIn = useSignIn<User>();

  const loginMutation = useMutation({
    mutationFn: postLogin,
    onSuccess: (data) => {
      if (
        signIn({
          auth: {
            token: data?.data?.data.accessToken!,
            type: "bearer",
          },
          refresh: data?.data?.data?.refreshToken!,
          userState: data?.data?.data?.user,
        })
      ) {
        return goto("/");
      } else {
        console.error("could not sign in");
      }
    },
    onError: (error) => {
      console.error(error);
    },
  });

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const loginReq: components["schemas"]["LoginRequestDTO"] = {
      email,
      password: pwd,
    };
    loginMutation.mutate(loginReq);
  };

  return (
    <div className="h-full flex flex-col items-center">
      <h1>Login Page</h1>

      <form
        onSubmit={onSubmit}
        className="my-auto w-full flex flex-col items-center gap-4"
      >
        <div className="w-6/12">
          <label htmlFor="email" className="label">
            Email
          </label>
          <input
            type="email"
            id="email"
            className="input"
            value={email}
            onChange={(e) => {
              setEmail(e.currentTarget.value);
            }}
          />
        </div>
        <div className="w-6/12">
          <label htmlFor="password" className="label">
            Password
          </label>
          <input
            type="password"
            id="password"
            className="input"
            value={pwd}
            onChange={(e) => {
              setPwd(e.currentTarget.value);
            }}
          />
        </div>
        <button className="btn" type="submit">
          Login
        </button>
      </form>
    </div>
  );
};

export default LoginPage;
