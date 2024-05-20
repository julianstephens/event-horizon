import { Loader } from "@/components/Loader";
import { checkhealth, postLogin } from "@/hooks/queries";
import type { User } from "@/lib/api/aliases";
import { components } from "@/lib/api/api";
import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import useIsAuthenticated from "react-auth-kit/hooks/useIsAuthenticated";
import useSignIn from "react-auth-kit/hooks/useSignIn";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [email, setEmail] = useState("spidaman@theweb.net");
  const [pwd, setPwd] = useState("********");

  const goto = useNavigate();

  const { data, error, isLoading: checkLoading } = checkhealth();

  const signIn = useSignIn<User>();
  const isAuthed = useIsAuthenticated();

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
    setIsLoading(true);
    e.preventDefault();
    const loginReq: components["schemas"]["LoginRequestDTO"] = {
      email,
      password: pwd,
    };
    loginMutation.mutate(loginReq);
    setIsLoading(false);
  };

  useEffect(() => {
    if (!checkLoading && error) console.error(error);
    if (!checkLoading && data) console.log(data.data);
  }, [checkLoading]);

  useEffect(() => {
    if (isAuthed) goto("/dashboard");
  }, [isAuthed]);

  return (
    <div className="h-full flex flex-col items-center">
      <h1>Login Page</h1>
      {isLoading ? (
        <Loader />
      ) : (
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
      )}
    </div>
  );
};

export default LoginPage;
