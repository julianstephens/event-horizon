import createRefresh from "react-auth-kit/createRefresh";
import client from "./api";

const refreshApi = createRefresh({
  interval: 2700, // Refreshes the token in every 45 minutes
  refreshApiCallback: async ({ authToken }) => {
    try {
      const res = await client.POST("/auth/refresh", {
        headers: { Authorization: `Bearer ${authToken}` },
      });

      return {
        isSuccess: true,
        newAuthToken: res?.data?.data?.access_token!,
      };
    } catch (error) {
      console.error(error);

      return {
        isSuccess: false,
        newAuthToken: "",
      };
    }
  },
});

export default refreshApi;
