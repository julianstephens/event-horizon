import client from "@/lib/api";
import { useQuery } from "@tanstack/react-query";

export * from "./auth";
export * from "./events";
export * from "./users";

export const checkhealth = () => {
  return useQuery({
    queryKey: ["/"],
    queryFn: async ({ signal }) => {
      const { data } = await client.GET("/", {
        signal,
      });
      return data;
    },
  });
};
