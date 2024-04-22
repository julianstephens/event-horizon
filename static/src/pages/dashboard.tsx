import { deleteLogout } from "@/hooks/queries";
import { User } from "@/lib/api/aliases";
import { useMutation } from "@tanstack/react-query";
import useAuthUser from "react-auth-kit/hooks/useAuthUser";
import useSignOut from "react-auth-kit/hooks/useSignOut";
import toast from "react-hot-toast";

const DashboardPage = () => {
  const currUser = useAuthUser<User>();
  const signOut = useSignOut();

  const logoutMutation = useMutation({
    mutationFn: deleteLogout,
    onSuccess: () => {
      toast.success
      signOut();
    },
    onError: (error) => {
      console.error(error)
    }
  });

  return (
    <div className="row">
      <h1>Hello, {currUser?.fname ?? currUser?.email}</h1>
      <button
        className="btn"
        onClick={() => {
          logoutMutation.mutate();
        }}
      >
        Logout
      </button>
    </div>
  );
};

export default DashboardPage;
