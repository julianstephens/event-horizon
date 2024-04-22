import DashboardPage from "@/pages/dashboard";
import LoginPage from "@/pages/login";
import AuthOutlet from "@auth-kit/react-router/AuthOutlet";
import { BrowserRouter, Route, Routes } from "react-router-dom";

const AppRoutes = () => (
  <BrowserRouter>
    <Routes>
      <Route element={<AuthOutlet fallbackPath="/login" />}>
        <Route path="/" element={<DashboardPage />} />
      </Route>
      <Route path={"/login"} element={<LoginPage />} />
    </Routes>
  </BrowserRouter>
);

export default AppRoutes;
