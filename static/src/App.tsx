import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AuthProvider from "react-auth-kit";
import { Toaster } from "react-hot-toast";
import AppRoutes from "./components/Routes";
import store from "./lib/react-auth-store";

const queryClient = new QueryClient();

const App = () => (
  <AuthProvider store={store}>
    <QueryClientProvider client={queryClient}>
      <AppRoutes />
      <Toaster />
    </QueryClientProvider>
  </AuthProvider>
);

export default App;
